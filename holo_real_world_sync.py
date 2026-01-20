#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
HOLO REAL WORLD SYNC - Synchronisation mit der echten Welt
================================================================================

Dieses Modul synchronisiert die virtuelle Welt von Holocloude mit der echten Welt:
- Jahreszeit basierend auf echtem Datum (inkl. astronomischer Berechnung)
- Tag/Nacht-Zyklus basierend auf Sonnenauf-/untergang am aktuellen Standort
- Echtes Wetter von API (OpenWeatherMap oder Home Assistant)
- Mondphasen
- Temperatur, Luftfeuchtigkeit, Wind, etc.

Autor: Holocloude Team
Version: 1.0.0
"""

import asyncio
import aiohttp
import json
import math
import logging
import os
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from pathlib import Path
import threading

# Logging Setup
logger = logging.getLogger("HoloRealWorldSync")


# =============================================================================
# ENUMS FÜR WELT-ZUSTÄNDE
# =============================================================================

class Season(Enum):
    """Jahreszeiten mit deutschen Namen und Eigenschaften."""
    FRUEHLING = ("Frühling", "spring", 3, 5)
    SOMMER = ("Sommer", "summer", 6, 8)
    HERBST = ("Herbst", "autumn", 9, 11)
    WINTER = ("Winter", "winter", 12, 2)

    def __init__(self, german: str, english: str, start_month: int, end_month: int):
        self.german = german
        self.english = english
        self.start_month = start_month
        self.end_month = end_month


class DayPhase(Enum):
    """Tageszeiten basierend auf Sonnenstand."""
    NACHT = ("Nacht", "night", 0.0, 0.0)
    DAEMMERUNG_MORGEN = ("Morgendämmerung", "dawn", 0.1, 0.3)
    SONNENAUFGANG = ("Sonnenaufgang", "sunrise", 0.3, 0.4)
    MORGEN = ("Morgen", "morning", 0.4, 0.5)
    VORMITTAG = ("Vormittag", "late_morning", 0.5, 0.6)
    MITTAG = ("Mittag", "noon", 0.6, 0.65)
    NACHMITTAG = ("Nachmittag", "afternoon", 0.65, 0.75)
    SPAETNACHMITTAG = ("Spätnachmittag", "late_afternoon", 0.75, 0.85)
    SONNENUNTERGANG = ("Sonnenuntergang", "sunset", 0.85, 0.95)
    DAEMMERUNG_ABEND = ("Abenddämmerung", "dusk", 0.95, 1.0)

    def __init__(self, german: str, english: str, day_progress_min: float, day_progress_max: float):
        self.german = german
        self.english = english
        self.day_progress_min = day_progress_min
        self.day_progress_max = day_progress_max


class MoonPhase(Enum):
    """Mondphasen."""
    NEUMOND = ("Neumond", "new_moon", "🌑")
    ZUNEHMENDE_SICHEL = ("Zunehmende Sichel", "waxing_crescent", "🌒")
    ERSTES_VIERTEL = ("Erstes Viertel", "first_quarter", "🌓")
    ZUNEHMENDER_MOND = ("Zunehmender Mond", "waxing_gibbous", "🌔")
    VOLLMOND = ("Vollmond", "full_moon", "🌕")
    ABNEHMENDER_MOND = ("Abnehmender Mond", "waning_gibbous", "🌖")
    LETZTES_VIERTEL = ("Letztes Viertel", "last_quarter", "🌗")
    ABNEHMENDE_SICHEL = ("Abnehmende Sichel", "waning_crescent", "🌘")

    def __init__(self, german: str, english: str, emoji: str):
        self.german = german
        self.english = english
        self.emoji = emoji


class WeatherCondition(Enum):
    """Wetterbedingungen."""
    KLAR = ("Klar", "clear", "☀️")
    TEILWEISE_BEWOELKT = ("Teilweise bewölkt", "partly_cloudy", "⛅")
    BEWOELKT = ("Bewölkt", "cloudy", "☁️")
    BEDECKT = ("Bedeckt", "overcast", "🌥️")
    NEBEL = ("Nebel", "fog", "🌫️")
    NIESELREGEN = ("Nieselregen", "drizzle", "🌦️")
    REGEN = ("Regen", "rain", "🌧️")
    STARKREGEN = ("Starkregen", "heavy_rain", "⛈️")
    GEWITTER = ("Gewitter", "thunderstorm", "🌩️")
    SCHNEE = ("Schnee", "snow", "❄️")
    SCHNEEREGEN = ("Schneeregen", "sleet", "🌨️")
    HAGEL = ("Hagel", "hail", "🧊")
    WIND = ("Windig", "windy", "💨")
    STURM = ("Sturm", "storm", "🌪️")

    def __init__(self, german: str, english: str, emoji: str):
        self.german = german
        self.english = english
        self.emoji = emoji


# =============================================================================
# DATENKLASSEN FÜR WELT-ZUSTAND
# =============================================================================

@dataclass
class SunPosition:
    """Position der Sonne am Himmel."""
    altitude: float  # Höhe über Horizont in Grad (-90 bis 90)
    azimuth: float   # Richtung in Grad (0 = Nord, 90 = Ost, etc.)
    is_up: bool      # Ist die Sonne über dem Horizont?
    sunrise: datetime
    sunset: datetime
    solar_noon: datetime
    day_length_hours: float

    @property
    def day_progress(self) -> float:
        """Fortschritt des Tages von Sonnenaufgang (0) bis Sonnenuntergang (1)."""
        now = datetime.now()
        if now < self.sunrise:
            return 0.0
        elif now > self.sunset:
            return 1.0
        else:
            total_seconds = (self.sunset - self.sunrise).total_seconds()
            elapsed_seconds = (now - self.sunrise).total_seconds()
            return elapsed_seconds / total_seconds if total_seconds > 0 else 0.5


@dataclass
class WeatherData:
    """Aktuelle Wetterdaten."""
    condition: WeatherCondition
    temperature_celsius: float
    feels_like_celsius: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_kmh: float
    wind_direction_degrees: int
    wind_gust_kmh: Optional[float] = None
    visibility_km: float = 10.0
    cloud_cover_percent: float = 0.0
    uv_index: float = 0.0
    precipitation_mm: float = 0.0
    description: str = ""
    icon: str = ""

    @property
    def temperature_description(self) -> str:
        """Beschreibung der Temperatur."""
        t = self.temperature_celsius
        if t < -10:
            return "eisig"
        elif t < 0:
            return "frostig"
        elif t < 5:
            return "sehr kalt"
        elif t < 10:
            return "kalt"
        elif t < 15:
            return "kühl"
        elif t < 20:
            return "mild"
        elif t < 25:
            return "angenehm warm"
        elif t < 30:
            return "warm"
        elif t < 35:
            return "heiß"
        else:
            return "sehr heiß"

    @property
    def wind_description(self) -> str:
        """Beschreibung der Windstärke nach Beaufort."""
        ws = self.wind_speed_kmh
        if ws < 1:
            return "windstill"
        elif ws < 6:
            return "leiser Zug"
        elif ws < 12:
            return "leichte Brise"
        elif ws < 20:
            return "schwache Brise"
        elif ws < 29:
            return "mäßige Brise"
        elif ws < 39:
            return "frische Brise"
        elif ws < 50:
            return "starker Wind"
        elif ws < 62:
            return "steifer Wind"
        elif ws < 75:
            return "stürmischer Wind"
        elif ws < 89:
            return "Sturm"
        elif ws < 103:
            return "schwerer Sturm"
        elif ws < 118:
            return "orkanartiger Sturm"
        else:
            return "Orkan"


@dataclass
class Location:
    """Standort-Konfiguration."""
    latitude: float
    longitude: float
    timezone: str = "Europe/Berlin"
    city: str = "Berlin"
    country: str = "DE"
    altitude_m: float = 0.0


@dataclass
class RealWorldState:
    """Gesamtzustand der echten Welt."""
    timestamp: datetime
    location: Location

    # Zeit & Datum
    season: Season
    season_progress: float  # 0-1, wie weit in der Jahreszeit
    day_phase: DayPhase
    is_daytime: bool
    is_weekend: bool
    is_holiday: bool
    holiday_name: Optional[str]

    # Sonne
    sun: SunPosition

    # Mond
    moon_phase: MoonPhase
    moon_illumination: float  # 0-100%
    moon_age_days: float

    # Wetter
    weather: WeatherData

    # Astronomische Infos
    is_astronomical_night: bool  # Sonne mehr als 18° unter Horizont
    is_nautical_twilight: bool   # Sonne 6-12° unter Horizont
    is_civil_twilight: bool      # Sonne 0-6° unter Horizont

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für Speicherung/Übertragung."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "location": asdict(self.location),
            "season": {
                "name": self.season.german,
                "english": self.season.english,
                "progress": self.season_progress
            },
            "time": {
                "phase": self.day_phase.german,
                "phase_english": self.day_phase.english,
                "is_daytime": self.is_daytime,
                "is_weekend": self.is_weekend,
                "is_holiday": self.is_holiday,
                "holiday_name": self.holiday_name
            },
            "sun": {
                "altitude": self.sun.altitude,
                "azimuth": self.sun.azimuth,
                "is_up": self.sun.is_up,
                "sunrise": self.sun.sunrise.isoformat(),
                "sunset": self.sun.sunset.isoformat(),
                "day_length_hours": self.sun.day_length_hours
            },
            "moon": {
                "phase": self.moon_phase.german,
                "emoji": self.moon_phase.emoji,
                "illumination": self.moon_illumination,
                "age_days": self.moon_age_days
            },
            "weather": asdict(self.weather) if self.weather else None,
            "twilight": {
                "astronomical_night": self.is_astronomical_night,
                "nautical_twilight": self.is_nautical_twilight,
                "civil_twilight": self.is_civil_twilight
            }
        }

    def get_atmosphere_description(self) -> str:
        """Generiert eine atmosphärische Beschreibung der aktuellen Welt."""
        parts = []

        # Zeit und Licht
        if self.is_daytime:
            if self.day_phase == DayPhase.MORGEN:
                parts.append(f"Der {self.season.german}smorgen erwacht")
            elif self.day_phase == DayPhase.MITTAG:
                parts.append(f"Die {self.season.german}ssonne steht hoch")
            elif self.day_phase in [DayPhase.SONNENAUFGANG, DayPhase.DAEMMERUNG_MORGEN]:
                parts.append(f"Die Sonne geht gerade auf")
            elif self.day_phase in [DayPhase.SONNENUNTERGANG, DayPhase.DAEMMERUNG_ABEND]:
                parts.append(f"Die Sonne neigt sich dem Horizont zu")
            else:
                parts.append(f"Es ist {self.day_phase.german}")
        else:
            parts.append(f"Es ist {self.day_phase.german}")
            parts.append(f"Der {self.moon_phase.emoji} {self.moon_phase.german} steht am Himmel")

        # Wetter
        if self.weather:
            parts.append(f"Das Wetter ist {self.weather.condition.german.lower()}")
            parts.append(f"bei {self.weather.temperature_celsius:.1f}°C ({self.weather.temperature_description})")
            if self.weather.wind_speed_kmh > 10:
                parts.append(f"mit {self.weather.wind_description}")

        return ". ".join(parts) + "."


# =============================================================================
# ASTRONOMISCHE BERECHNUNGEN
# =============================================================================

class AstronomyCalculator:
    """Berechnet astronomische Daten (Sonne, Mond, etc.)."""

    # Bekannter Neumond als Referenz (1. Januar 2000, 18:14 UTC)
    KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    LUNAR_CYCLE_DAYS = 29.530588853  # Synodischer Monat

    @classmethod
    def calculate_sun_position(cls, lat: float, lon: float, dt: datetime = None) -> SunPosition:
        """Berechnet die Position der Sonne am Himmel."""
        if dt is None:
            dt = datetime.now()

        # Julianisches Datum
        jd = cls._datetime_to_julian(dt)

        # Sonnenposition berechnen
        altitude, azimuth = cls._calc_sun_position_detailed(lat, lon, jd)

        # Sonnenauf- und -untergang
        sunrise, sunset, solar_noon = cls._calculate_sun_times(lat, lon, dt.date())

        # Tageslänge
        if sunrise and sunset:
            day_length = (sunset - sunrise).total_seconds() / 3600.0
        else:
            day_length = 12.0  # Fallback

        return SunPosition(
            altitude=altitude,
            azimuth=azimuth,
            is_up=altitude > 0,
            sunrise=sunrise or dt.replace(hour=6, minute=0),
            sunset=sunset or dt.replace(hour=18, minute=0),
            solar_noon=solar_noon or dt.replace(hour=12, minute=0),
            day_length_hours=day_length
        )

    @classmethod
    def _datetime_to_julian(cls, dt: datetime) -> float:
        """Konvertiert datetime zu Julianischem Datum."""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3

        jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

        # Tageszeit hinzufügen
        fraction = (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
        return jdn + fraction - 0.5

    @classmethod
    def _calc_sun_position_detailed(cls, lat: float, lon: float, jd: float) -> Tuple[float, float]:
        """Detaillierte Sonnenpositionsberechnung."""
        # Tage seit J2000.0
        n = jd - 2451545.0

        # Mittlere Länge der Sonne
        L = (280.460 + 0.9856474 * n) % 360

        # Mittlere Anomalie der Sonne
        g = math.radians((357.528 + 0.9856003 * n) % 360)

        # Ekliptikale Länge
        lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))

        # Schiefe der Ekliptik
        epsilon = math.radians(23.439 - 0.0000004 * n)

        # Rektaszension und Deklination
        sin_lambda = math.sin(lambda_sun)
        cos_lambda = math.cos(lambda_sun)
        sin_eps = math.sin(epsilon)
        cos_eps = math.cos(epsilon)

        # Deklination
        declination = math.asin(sin_eps * sin_lambda)

        # Rektaszension
        ra = math.atan2(cos_eps * sin_lambda, cos_lambda)

        # Sternzeit
        gmst = (280.46061837 + 360.98564736629 * n) % 360
        lst = math.radians((gmst + lon) % 360)

        # Stundenwinkel
        ha = lst - ra

        # Höhe und Azimut
        lat_rad = math.radians(lat)
        sin_lat = math.sin(lat_rad)
        cos_lat = math.cos(lat_rad)
        sin_dec = math.sin(declination)
        cos_dec = math.cos(declination)
        cos_ha = math.cos(ha)
        sin_ha = math.sin(ha)

        # Altitude (Höhe)
        altitude = math.degrees(math.asin(sin_lat * sin_dec + cos_lat * cos_dec * cos_ha))

        # Azimut
        azimuth = math.degrees(math.atan2(-sin_ha * cos_dec,
                                          cos_lat * sin_dec - sin_lat * cos_dec * cos_ha))
        azimuth = (azimuth + 360) % 360

        return altitude, azimuth

    @classmethod
    def _calculate_sun_times(cls, lat: float, lon: float, date) -> Tuple[datetime, datetime, datetime]:
        """Berechnet Sonnenauf-/untergang und Sonnenhöchststand."""
        # Vereinfachte Berechnung basierend auf NOAA-Algorithmus

        # Tag des Jahres
        day_of_year = date.timetuple().tm_yday

        # Zeitgleichung (Equation of Time) in Minuten
        b = math.radians(360.0 / 365.0 * (day_of_year - 81))
        eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)

        # Deklination der Sonne
        decl = math.radians(23.45 * math.sin(math.radians(360.0 / 365.0 * (day_of_year - 81))))

        # Stundenwinkel bei Sonnenauf-/untergang
        lat_rad = math.radians(lat)

        try:
            cos_ha = -math.tan(lat_rad) * math.tan(decl)
            cos_ha = max(-1, min(1, cos_ha))  # Clamping
            ha = math.degrees(math.acos(cos_ha))
        except:
            # Mitternachtssonne oder Polarnacht
            ha = 90 if day_of_year > 80 and day_of_year < 265 else 0

        # Sonnenhöchststand (Solar Noon) in UTC
        solar_noon_minutes = 720 - 4 * lon - eot

        # Sonnenaufgang und -untergang
        sunrise_minutes = solar_noon_minutes - ha * 4
        sunset_minutes = solar_noon_minutes + ha * 4

        # In datetime konvertieren
        base = datetime.combine(date, datetime.min.time())

        sunrise = base + timedelta(minutes=sunrise_minutes)
        sunset = base + timedelta(minutes=sunset_minutes)
        solar_noon = base + timedelta(minutes=solar_noon_minutes)

        return sunrise, sunset, solar_noon

    @classmethod
    def calculate_moon_phase(cls, dt: datetime = None) -> Tuple[MoonPhase, float, float]:
        """Berechnet die aktuelle Mondphase."""
        if dt is None:
            dt = datetime.now(timezone.utc)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # Tage seit bekanntem Neumond
        diff = (dt - cls.KNOWN_NEW_MOON).total_seconds() / 86400.0

        # Position im aktuellen Zyklus
        moon_age = diff % cls.LUNAR_CYCLE_DAYS

        # Beleuchtung (Näherung)
        phase_fraction = moon_age / cls.LUNAR_CYCLE_DAYS
        illumination = (1 - math.cos(2 * math.pi * phase_fraction)) / 2 * 100

        # Mondphase bestimmen
        phase_index = int((phase_fraction * 8) % 8)
        phases = [
            MoonPhase.NEUMOND,
            MoonPhase.ZUNEHMENDE_SICHEL,
            MoonPhase.ERSTES_VIERTEL,
            MoonPhase.ZUNEHMENDER_MOND,
            MoonPhase.VOLLMOND,
            MoonPhase.ABNEHMENDER_MOND,
            MoonPhase.LETZTES_VIERTEL,
            MoonPhase.ABNEHMENDE_SICHEL
        ]

        return phases[phase_index], illumination, moon_age


# =============================================================================
# WETTER-DIENSTE
# =============================================================================

class WeatherService:
    """Abstrakte Basis für Wetterdienste."""

    async def get_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        raise NotImplementedError


class OpenWeatherMapService(WeatherService):
    """OpenWeatherMap API Integration."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _map_condition(self, weather_id: int, icon: str) -> WeatherCondition:
        """Mappt OpenWeatherMap Wetter-ID zu WeatherCondition."""
        # Thunderstorm (2xx)
        if 200 <= weather_id < 300:
            return WeatherCondition.GEWITTER
        # Drizzle (3xx)
        elif 300 <= weather_id < 400:
            return WeatherCondition.NIESELREGEN
        # Rain (5xx)
        elif 500 <= weather_id < 510:
            return WeatherCondition.REGEN
        elif 510 <= weather_id < 520:
            return WeatherCondition.STARKREGEN
        elif 520 <= weather_id < 600:
            return WeatherCondition.REGEN
        # Snow (6xx)
        elif 600 <= weather_id < 620:
            return WeatherCondition.SCHNEE
        elif 620 <= weather_id < 630:
            return WeatherCondition.SCHNEEREGEN
        # Atmosphere (7xx)
        elif 700 <= weather_id < 800:
            return WeatherCondition.NEBEL
        # Clear (800)
        elif weather_id == 800:
            return WeatherCondition.KLAR
        # Clouds (8xx)
        elif weather_id == 801:
            return WeatherCondition.TEILWEISE_BEWOELKT
        elif weather_id == 802:
            return WeatherCondition.BEWOELKT
        elif weather_id >= 803:
            return WeatherCondition.BEDECKT
        else:
            return WeatherCondition.KLAR

    async def get_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Ruft aktuelle Wetterdaten von OpenWeatherMap ab."""
        if not self.api_key:
            logger.warning("OpenWeatherMap API Key nicht konfiguriert")
            return None

        try:
            session = await self._get_session()
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "lang": "de"
            }

            async with session.get(self.BASE_URL, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data)
                else:
                    logger.error(f"OpenWeatherMap API Fehler: {response.status}")
                    return None

        except asyncio.TimeoutError:
            logger.error("OpenWeatherMap API Timeout")
            return None
        except Exception as e:
            logger.error(f"OpenWeatherMap API Fehler: {e}")
            return None

    def _parse_response(self, data: Dict) -> WeatherData:
        """Parsed OpenWeatherMap API Response."""
        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})

        return WeatherData(
            condition=self._map_condition(weather.get("id", 800), weather.get("icon", "")),
            temperature_celsius=main.get("temp", 20.0),
            feels_like_celsius=main.get("feels_like", 20.0),
            humidity_percent=main.get("humidity", 50.0),
            pressure_hpa=main.get("pressure", 1013.0),
            wind_speed_kmh=wind.get("speed", 0) * 3.6,  # m/s zu km/h
            wind_direction_degrees=wind.get("deg", 0),
            wind_gust_kmh=wind.get("gust", 0) * 3.6 if wind.get("gust") else None,
            visibility_km=data.get("visibility", 10000) / 1000,
            cloud_cover_percent=clouds.get("all", 0),
            description=weather.get("description", ""),
            icon=weather.get("icon", "")
        )


class HomeAssistantWeatherService(WeatherService):
    """Home Assistant Wetter-Entity Integration."""

    def __init__(self, api_url: str, token: str, entity_id: str = "weather.home"):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.entity_id = entity_id
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _map_state(self, state: str) -> WeatherCondition:
        """Mappt Home Assistant Wetter-Zustand zu WeatherCondition."""
        state_map = {
            "clear-night": WeatherCondition.KLAR,
            "cloudy": WeatherCondition.BEWOELKT,
            "exceptional": WeatherCondition.KLAR,
            "fog": WeatherCondition.NEBEL,
            "hail": WeatherCondition.HAGEL,
            "lightning": WeatherCondition.GEWITTER,
            "lightning-rainy": WeatherCondition.GEWITTER,
            "partlycloudy": WeatherCondition.TEILWEISE_BEWOELKT,
            "pouring": WeatherCondition.STARKREGEN,
            "rainy": WeatherCondition.REGEN,
            "snowy": WeatherCondition.SCHNEE,
            "snowy-rainy": WeatherCondition.SCHNEEREGEN,
            "sunny": WeatherCondition.KLAR,
            "windy": WeatherCondition.WIND,
            "windy-variant": WeatherCondition.WIND,
        }
        return state_map.get(state, WeatherCondition.KLAR)

    async def get_weather(self, lat: float = None, lon: float = None) -> Optional[WeatherData]:
        """Ruft Wetterdaten von Home Assistant ab."""
        if not self.token:
            logger.warning("Home Assistant Token nicht konfiguriert")
            return None

        try:
            session = await self._get_session()
            url = f"{self.api_url}/states/{self.entity_id}"

            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_response(data)
                else:
                    logger.error(f"Home Assistant API Fehler: {response.status}")
                    return None

        except asyncio.TimeoutError:
            logger.error("Home Assistant API Timeout")
            return None
        except Exception as e:
            logger.error(f"Home Assistant API Fehler: {e}")
            return None

    def _parse_response(self, data: Dict) -> WeatherData:
        """Parsed Home Assistant Weather Entity Response."""
        attrs = data.get("attributes", {})
        state = data.get("state", "sunny")

        return WeatherData(
            condition=self._map_state(state),
            temperature_celsius=attrs.get("temperature", 20.0),
            feels_like_celsius=attrs.get("temperature", 20.0),  # HA hat kein feels_like
            humidity_percent=attrs.get("humidity", 50.0),
            pressure_hpa=attrs.get("pressure", 1013.0),
            wind_speed_kmh=attrs.get("wind_speed", 0),
            wind_direction_degrees=attrs.get("wind_bearing", 0),
            visibility_km=attrs.get("visibility", 10.0),
            description=state,
            icon=""
        )


class SimulatedWeatherService(WeatherService):
    """Simulierter Wetterdienst basierend auf Jahreszeit und Tageszeit (Fallback)."""

    def __init__(self, location: Location):
        self.location = location

    async def get_weather(self, lat: float = None, lon: float = None) -> WeatherData:
        """Generiert simuliertes Wetter basierend auf Jahreszeit."""
        import random

        now = datetime.now()
        month = now.month
        hour = now.hour

        # Basis-Temperaturen nach Jahreszeit (für Deutschland)
        season_temps = {
            1: (-2, 4),    # Januar
            2: (-1, 5),    # Februar
            3: (2, 10),    # März
            4: (5, 15),    # April
            5: (9, 19),    # Mai
            6: (12, 23),   # Juni
            7: (14, 25),   # Juli
            8: (14, 24),   # August
            9: (10, 20),   # September
            10: (6, 14),   # Oktober
            11: (2, 8),    # November
            12: (-1, 4),   # Dezember
        }

        min_temp, max_temp = season_temps.get(month, (10, 20))

        # Tagesverlauf der Temperatur
        if 6 <= hour <= 14:
            # Aufwärmphase
            progress = (hour - 6) / 8
            temp = min_temp + (max_temp - min_temp) * progress
        elif 14 < hour <= 20:
            # Abkühlphase
            progress = (hour - 14) / 6
            temp = max_temp - (max_temp - min_temp) * progress * 0.5
        else:
            # Nacht
            temp = min_temp + random.uniform(-2, 2)

        # Leichte Variation
        temp += random.uniform(-1, 1)

        # Wetterbedingung nach Jahreszeit
        season_conditions = {
            "winter": [
                (WeatherCondition.BEWOELKT, 30),
                (WeatherCondition.BEDECKT, 25),
                (WeatherCondition.SCHNEE, 15),
                (WeatherCondition.REGEN, 10),
                (WeatherCondition.NEBEL, 10),
                (WeatherCondition.KLAR, 10),
            ],
            "fruehling": [
                (WeatherCondition.TEILWEISE_BEWOELKT, 30),
                (WeatherCondition.KLAR, 25),
                (WeatherCondition.REGEN, 20),
                (WeatherCondition.BEWOELKT, 15),
                (WeatherCondition.GEWITTER, 10),
            ],
            "sommer": [
                (WeatherCondition.KLAR, 35),
                (WeatherCondition.TEILWEISE_BEWOELKT, 25),
                (WeatherCondition.GEWITTER, 15),
                (WeatherCondition.BEWOELKT, 15),
                (WeatherCondition.REGEN, 10),
            ],
            "herbst": [
                (WeatherCondition.BEWOELKT, 30),
                (WeatherCondition.REGEN, 25),
                (WeatherCondition.NEBEL, 15),
                (WeatherCondition.TEILWEISE_BEWOELKT, 15),
                (WeatherCondition.KLAR, 10),
                (WeatherCondition.WIND, 5),
            ],
        }

        # Aktuelle Jahreszeit
        if month in [12, 1, 2]:
            season_key = "winter"
        elif month in [3, 4, 5]:
            season_key = "fruehling"
        elif month in [6, 7, 8]:
            season_key = "sommer"
        else:
            season_key = "herbst"

        # Zufällige Wetterbedingung
        conditions = season_conditions[season_key]
        total_weight = sum(w for _, w in conditions)
        r = random.uniform(0, total_weight)
        cumulative = 0
        condition = WeatherCondition.KLAR
        for cond, weight in conditions:
            cumulative += weight
            if r <= cumulative:
                condition = cond
                break

        # Wind
        wind_speed = random.uniform(0, 30)
        if condition in [WeatherCondition.STURM, WeatherCondition.GEWITTER]:
            wind_speed = random.uniform(40, 80)
        elif condition == WeatherCondition.WIND:
            wind_speed = random.uniform(30, 50)

        return WeatherData(
            condition=condition,
            temperature_celsius=round(temp, 1),
            feels_like_celsius=round(temp - wind_speed / 10, 1),
            humidity_percent=random.uniform(40, 90),
            pressure_hpa=random.uniform(990, 1030),
            wind_speed_kmh=round(wind_speed, 1),
            wind_direction_degrees=random.randint(0, 360),
            visibility_km=random.uniform(5, 20),
            cloud_cover_percent=random.uniform(0, 100) if condition != WeatherCondition.KLAR else random.uniform(0, 20),
            description=f"Simuliert: {condition.german}",
            icon=""
        )


# =============================================================================
# DEUTSCHE FEIERTAGE
# =============================================================================

class GermanHolidays:
    """Berechnet deutsche Feiertage (bundesweit und bewegliche)."""

    @classmethod
    def get_holidays(cls, year: int) -> Dict[Tuple[int, int], str]:
        """Gibt alle Feiertage für ein Jahr zurück."""
        holidays = {
            # Feste Feiertage
            (1, 1): "Neujahr",
            (5, 1): "Tag der Arbeit",
            (10, 3): "Tag der Deutschen Einheit",
            (12, 25): "1. Weihnachtstag",
            (12, 26): "2. Weihnachtstag",
        }

        # Bewegliche Feiertage basierend auf Ostern
        easter = cls._calculate_easter(year)

        # Karfreitag (2 Tage vor Ostern)
        karfreitag = easter - timedelta(days=2)
        holidays[(karfreitag.month, karfreitag.day)] = "Karfreitag"

        # Ostersonntag
        holidays[(easter.month, easter.day)] = "Ostersonntag"

        # Ostermontag
        ostermontag = easter + timedelta(days=1)
        holidays[(ostermontag.month, ostermontag.day)] = "Ostermontag"

        # Christi Himmelfahrt (39 Tage nach Ostern)
        himmelfahrt = easter + timedelta(days=39)
        holidays[(himmelfahrt.month, himmelfahrt.day)] = "Christi Himmelfahrt"

        # Pfingstsonntag (49 Tage nach Ostern)
        pfingstsonntag = easter + timedelta(days=49)
        holidays[(pfingstsonntag.month, pfingstsonntag.day)] = "Pfingstsonntag"

        # Pfingstmontag (50 Tage nach Ostern)
        pfingstmontag = easter + timedelta(days=50)
        holidays[(pfingstmontag.month, pfingstmontag.day)] = "Pfingstmontag"

        return holidays

    @classmethod
    def _calculate_easter(cls, year: int) -> datetime:
        """Berechnet das Osterdatum mit dem Gauß-Algorithmus."""
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1

        return datetime(year, month, day)

    @classmethod
    def is_holiday(cls, dt: datetime = None) -> Tuple[bool, Optional[str]]:
        """Prüft ob ein Datum ein Feiertag ist."""
        if dt is None:
            dt = datetime.now()

        holidays = cls.get_holidays(dt.year)
        key = (dt.month, dt.day)

        if key in holidays:
            return True, holidays[key]
        return False, None


# =============================================================================
# HAUPTKLASSE: REAL WORLD SYNC
# =============================================================================

class RealWorldSync:
    """Hauptklasse für die Synchronisation mit der echten Welt."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialisiert den Real World Sync.

        Args:
            config: Konfiguration mit API-Keys, Standort, etc.
        """
        self.config = config or {}

        # Standort initialisieren
        location_config = self.config.get("location", {})
        self.location = Location(
            latitude=location_config.get("latitude", 52.5200),  # Berlin default
            longitude=location_config.get("longitude", 13.4050),
            timezone=location_config.get("timezone", "Europe/Berlin"),
            city=location_config.get("city", "Berlin"),
            country=location_config.get("country", "DE"),
            altitude_m=location_config.get("altitude_m", 34.0)
        )

        # Wetter-Services initialisieren
        self._init_weather_services()

        # Cache für Wetterdaten
        self._weather_cache: Optional[WeatherData] = None
        self._weather_cache_time: Optional[datetime] = None
        self._weather_cache_duration = timedelta(minutes=15)

        # Aktueller Weltzustand
        self._current_state: Optional[RealWorldState] = None
        self._state_lock = threading.Lock()

        # Update-Task
        self._update_task: Optional[asyncio.Task] = None
        self._running = False

        logger.info(f"RealWorldSync initialisiert für {self.location.city}, {self.location.country}")

    def _init_weather_services(self):
        """Initialisiert die Wetter-Services nach Priorität."""
        self.weather_services: List[WeatherService] = []

        # OpenWeatherMap
        owm_key = self.config.get("openweathermap_api_key") or os.getenv("OPENWEATHERMAP_API_KEY")
        if owm_key:
            self.weather_services.append(OpenWeatherMapService(owm_key))
            logger.info("OpenWeatherMap Service aktiviert")

        # Home Assistant
        ha_config = self.config.get("home_assistant", {})
        ha_url = ha_config.get("api_url") or os.getenv("HOME_ASSISTANT_URL")
        ha_token = ha_config.get("token") or os.getenv("HOME_ASSISTANT_TOKEN")
        if ha_url and ha_token:
            entity = ha_config.get("weather_entity", "weather.home")
            self.weather_services.append(HomeAssistantWeatherService(ha_url, ha_token, entity))
            logger.info("Home Assistant Weather Service aktiviert")

        # Fallback: Simuliertes Wetter
        self.weather_services.append(SimulatedWeatherService(self.location))
        logger.info("Simulierter Weather Service als Fallback aktiviert")

    def get_season(self, dt: datetime = None) -> Tuple[Season, float]:
        """
        Ermittelt die aktuelle Jahreszeit.

        Returns:
            Tuple aus Season und Fortschritt (0-1) innerhalb der Jahreszeit
        """
        if dt is None:
            dt = datetime.now()

        month = dt.month
        day = dt.day

        # Jahreszeit bestimmen
        if month in [3, 4, 5]:
            season = Season.FRUEHLING
            # Fortschritt: März = 0, Ende Mai = 1
            days_in_season = 92  # ca. Tage im Frühling
            day_of_season = (month - 3) * 31 + day
        elif month in [6, 7, 8]:
            season = Season.SOMMER
            days_in_season = 92
            day_of_season = (month - 6) * 31 + day
        elif month in [9, 10, 11]:
            season = Season.HERBST
            days_in_season = 91
            day_of_season = (month - 9) * 31 + day
        else:  # 12, 1, 2
            season = Season.WINTER
            days_in_season = 90
            if month == 12:
                day_of_season = day
            elif month == 1:
                day_of_season = 31 + day
            else:  # Februar
                day_of_season = 62 + day

        progress = min(1.0, day_of_season / days_in_season)

        return season, progress

    def get_day_phase(self, sun: SunPosition) -> DayPhase:
        """Ermittelt die aktuelle Tagesphase basierend auf Sonnenposition."""
        now = datetime.now()

        # Vor Sonnenaufgang
        if now < sun.sunrise - timedelta(minutes=30):
            return DayPhase.NACHT
        elif now < sun.sunrise:
            return DayPhase.DAEMMERUNG_MORGEN
        elif now < sun.sunrise + timedelta(minutes=30):
            return DayPhase.SONNENAUFGANG
        # Nach Sonnenuntergang
        elif now > sun.sunset + timedelta(minutes=30):
            return DayPhase.NACHT
        elif now > sun.sunset:
            return DayPhase.DAEMMERUNG_ABEND
        elif now > sun.sunset - timedelta(minutes=30):
            return DayPhase.SONNENUNTERGANG
        else:
            # Tagsüber: basierend auf Fortschritt
            progress = sun.day_progress
            hour = now.hour

            if hour < 10:
                return DayPhase.MORGEN
            elif hour < 12:
                return DayPhase.VORMITTAG
            elif hour < 14:
                return DayPhase.MITTAG
            elif hour < 16:
                return DayPhase.NACHMITTAG
            else:
                return DayPhase.SPAETNACHMITTAG

    async def get_weather(self, force_refresh: bool = False) -> Optional[WeatherData]:
        """
        Holt aktuelle Wetterdaten (mit Caching).

        Args:
            force_refresh: Cache ignorieren und neu abrufen
        """
        # Cache prüfen
        if not force_refresh and self._weather_cache and self._weather_cache_time:
            if datetime.now() - self._weather_cache_time < self._weather_cache_duration:
                return self._weather_cache

        # Wetter von Services abrufen
        for service in self.weather_services:
            try:
                weather = await service.get_weather(self.location.latitude, self.location.longitude)
                if weather:
                    self._weather_cache = weather
                    self._weather_cache_time = datetime.now()
                    logger.debug(f"Wetter aktualisiert via {service.__class__.__name__}")
                    return weather
            except Exception as e:
                logger.warning(f"Fehler bei {service.__class__.__name__}: {e}")
                continue

        logger.error("Keine Wetterdaten verfügbar")
        return None

    async def get_current_state(self, force_refresh: bool = False) -> RealWorldState:
        """
        Ermittelt den aktuellen Zustand der echten Welt.

        Args:
            force_refresh: Alle Daten neu abrufen (nicht aus Cache)
        """
        now = datetime.now()

        # Jahreszeit
        season, season_progress = self.get_season(now)

        # Sonnenposition
        sun = AstronomyCalculator.calculate_sun_position(
            self.location.latitude,
            self.location.longitude,
            now
        )

        # Tagesphase
        day_phase = self.get_day_phase(sun)

        # Mondphase
        moon_phase, moon_illumination, moon_age = AstronomyCalculator.calculate_moon_phase(now)

        # Feiertag
        is_holiday, holiday_name = GermanHolidays.is_holiday(now)

        # Wetter
        weather = await self.get_weather(force_refresh)

        # Dämmerungszustände basierend auf Sonnenhöhe
        is_astronomical_night = sun.altitude < -18
        is_nautical_twilight = -18 <= sun.altitude < -12
        is_civil_twilight = -12 <= sun.altitude < -6

        state = RealWorldState(
            timestamp=now,
            location=self.location,
            season=season,
            season_progress=season_progress,
            day_phase=day_phase,
            is_daytime=sun.is_up,
            is_weekend=now.weekday() >= 5,
            is_holiday=is_holiday,
            holiday_name=holiday_name,
            sun=sun,
            moon_phase=moon_phase,
            moon_illumination=moon_illumination,
            moon_age_days=moon_age,
            weather=weather,
            is_astronomical_night=is_astronomical_night,
            is_nautical_twilight=is_nautical_twilight,
            is_civil_twilight=is_civil_twilight
        )

        with self._state_lock:
            self._current_state = state

        return state

    @property
    def current_state(self) -> Optional[RealWorldState]:
        """Gibt den aktuellen gecachten Zustand zurück."""
        with self._state_lock:
            return self._current_state

    async def start_auto_update(self, interval_seconds: int = 300):
        """Startet automatische Updates im Hintergrund."""
        self._running = True

        async def update_loop():
            while self._running:
                try:
                    await self.get_current_state(force_refresh=True)
                    logger.debug("Real World State aktualisiert")
                except Exception as e:
                    logger.error(f"Fehler beim Update: {e}")
                await asyncio.sleep(interval_seconds)

        self._update_task = asyncio.create_task(update_loop())
        logger.info(f"Auto-Update gestartet (Intervall: {interval_seconds}s)")

    async def stop_auto_update(self):
        """Stoppt die automatischen Updates."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        logger.info("Auto-Update gestoppt")

    async def close(self):
        """Schließt alle Verbindungen."""
        await self.stop_auto_update()
        for service in self.weather_services:
            if hasattr(service, 'close'):
                await service.close()

    # =========================================================================
    # HELPER METHODEN FÜR INTEGRATION
    # =========================================================================

    def get_time_of_day_simple(self) -> str:
        """Gibt einfache Tageszeit zurück (kompatibel mit holo_brain_core)."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Morgen"
        elif 12 <= hour < 14:
            return "Mittag"
        elif 14 <= hour < 18:
            return "Nachmittag"
        elif 18 <= hour < 22:
            return "Abend"
        else:
            return "Nacht"

    def get_season_simple(self) -> str:
        """Gibt einfache Jahreszeit zurück (kompatibel mit holo_brain_core)."""
        season, _ = self.get_season()
        return season.german

    def get_light_level(self) -> float:
        """
        Gibt den aktuellen Lichtlevel zurück (0.0 = dunkel, 1.0 = hell).
        Nützlich für Stimmungsanpassungen.
        """
        state = self.current_state
        if not state:
            # Fallback basierend auf Uhrzeit
            hour = datetime.now().hour
            if 6 <= hour <= 18:
                return 0.8
            elif 4 <= hour <= 6 or 18 <= hour <= 20:
                return 0.4
            else:
                return 0.1

        # Basierend auf Sonnenhöhe
        altitude = state.sun.altitude
        if altitude > 15:
            base_light = 1.0
        elif altitude > 0:
            base_light = 0.5 + (altitude / 30)
        elif altitude > -6:
            base_light = 0.2 + (altitude + 6) / 12
        elif altitude > -12:
            base_light = 0.1
        else:
            base_light = 0.0

        # Wetter-Modifikation
        if state.weather:
            cloud_factor = 1.0 - (state.weather.cloud_cover_percent / 200)  # Max -50%
            base_light *= cloud_factor

        return max(0.0, min(1.0, base_light))

    def get_mood_modifiers(self) -> Dict[str, float]:
        """
        Gibt Stimmungsmodifikatoren basierend auf Umwelt zurück.
        Kann in Emotional Engines verwendet werden.
        """
        modifiers = {}
        state = self.current_state

        if not state:
            return modifiers

        # Licht-basierte Modifikatoren
        light = self.get_light_level()
        if light > 0.7:
            modifiers["energy"] = 0.1
            modifiers["happiness"] = 0.05
        elif light < 0.3:
            modifiers["energy"] = -0.1
            modifiers["calmness"] = 0.1

        # Wetter-basierte Modifikatoren
        if state.weather:
            if state.weather.condition == WeatherCondition.KLAR:
                modifiers["happiness"] = modifiers.get("happiness", 0) + 0.1
            elif state.weather.condition in [WeatherCondition.REGEN, WeatherCondition.STARKREGEN]:
                modifiers["melancholy"] = 0.1
                modifiers["calmness"] = modifiers.get("calmness", 0) + 0.05
            elif state.weather.condition == WeatherCondition.GEWITTER:
                modifiers["excitement"] = 0.1
                modifiers["anxiety"] = 0.05
            elif state.weather.condition == WeatherCondition.SCHNEE:
                modifiers["wonder"] = 0.1
                modifiers["happiness"] = modifiers.get("happiness", 0) + 0.05

            # Temperatur
            if state.weather.temperature_celsius < 0:
                modifiers["discomfort"] = 0.1
            elif state.weather.temperature_celsius > 30:
                modifiers["energy"] = modifiers.get("energy", 0) - 0.1
                modifiers["irritability"] = 0.05

        # Jahreszeit
        if state.season == Season.FRUEHLING:
            modifiers["hope"] = 0.1
            modifiers["energy"] = modifiers.get("energy", 0) + 0.05
        elif state.season == Season.SOMMER:
            modifiers["happiness"] = modifiers.get("happiness", 0) + 0.05
        elif state.season == Season.HERBST:
            modifiers["melancholy"] = modifiers.get("melancholy", 0) + 0.05
            modifiers["contemplation"] = 0.1
        elif state.season == Season.WINTER:
            modifiers["coziness"] = 0.1

        # Feiertag
        if state.is_holiday:
            modifiers["happiness"] = modifiers.get("happiness", 0) + 0.1
            modifiers["relaxation"] = 0.1

        # Wochenende
        if state.is_weekend:
            modifiers["relaxation"] = modifiers.get("relaxation", 0) + 0.05

        # Mondphase (subtiler Einfluss)
        if state.moon_phase == MoonPhase.VOLLMOND:
            modifiers["mystical"] = 0.05
            modifiers["energy"] = modifiers.get("energy", 0) + 0.02

        return modifiers


# =============================================================================
# SINGLETON INSTANZ
# =============================================================================

_instance: Optional[RealWorldSync] = None
_instance_lock = threading.Lock()


def get_real_world_sync(config: Dict[str, Any] = None) -> RealWorldSync:
    """
    Gibt die Singleton-Instanz des RealWorldSync zurück.

    Args:
        config: Optionale Konfiguration (nur beim ersten Aufruf relevant)
    """
    global _instance

    with _instance_lock:
        if _instance is None:
            _instance = RealWorldSync(config)
        return _instance


def init_from_config_file(config_path: str = "config.json") -> RealWorldSync:
    """
    Initialisiert RealWorldSync aus einer Konfigurationsdatei.

    Args:
        config_path: Pfad zur Konfigurationsdatei
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            full_config = json.load(f)

        # Relevante Konfiguration extrahieren
        config = {
            "location": full_config.get("location", {}),
            "home_assistant": full_config.get("network", {}).get("home_assistant", {}),
            "openweathermap_api_key": full_config.get("weather", {}).get("openweathermap_api_key"),
        }

        return get_real_world_sync(config)

    except FileNotFoundError:
        logger.warning(f"Konfigurationsdatei {config_path} nicht gefunden, verwende Defaults")
        return get_real_world_sync({})
    except Exception as e:
        logger.error(f"Fehler beim Laden der Konfiguration: {e}")
        return get_real_world_sync({})


# =============================================================================
# CLI TEST
# =============================================================================

async def main():
    """Test-Funktion für CLI."""
    print("=" * 60)
    print("HOLO REAL WORLD SYNC - Test")
    print("=" * 60)

    # Mit Default-Konfiguration initialisieren
    sync = get_real_world_sync({
        "location": {
            "latitude": 52.5200,
            "longitude": 13.4050,
            "city": "Berlin",
            "country": "DE"
        }
    })

    # Aktuellen Zustand abrufen
    state = await sync.get_current_state()

    print(f"\nStandort: {state.location.city}, {state.location.country}")
    print(f"Zeit: {state.timestamp.strftime('%d.%m.%Y %H:%M:%S')}")
    print()

    print("--- JAHRESZEIT ---")
    print(f"Jahreszeit: {state.season.german}")
    print(f"Fortschritt: {state.season_progress*100:.1f}%")
    print()

    print("--- TAGESZEIT ---")
    print(f"Phase: {state.day_phase.german}")
    print(f"Tageslicht: {'Ja' if state.is_daytime else 'Nein'}")
    print(f"Sonnenaufgang: {state.sun.sunrise.strftime('%H:%M')}")
    print(f"Sonnenuntergang: {state.sun.sunset.strftime('%H:%M')}")
    print(f"Tageslänge: {state.sun.day_length_hours:.1f} Stunden")
    print(f"Lichtlevel: {sync.get_light_level()*100:.0f}%")
    print()

    print("--- MOND ---")
    print(f"Phase: {state.moon_phase.emoji} {state.moon_phase.german}")
    print(f"Beleuchtung: {state.moon_illumination:.0f}%")
    print(f"Alter: {state.moon_age_days:.1f} Tage")
    print()

    print("--- WETTER ---")
    if state.weather:
        print(f"Zustand: {state.weather.condition.emoji} {state.weather.condition.german}")
        print(f"Temperatur: {state.weather.temperature_celsius:.1f}°C ({state.weather.temperature_description})")
        print(f"Gefühlt: {state.weather.feels_like_celsius:.1f}°C")
        print(f"Luftfeuchtigkeit: {state.weather.humidity_percent:.0f}%")
        print(f"Wind: {state.weather.wind_speed_kmh:.1f} km/h ({state.weather.wind_description})")
        print(f"Bewölkung: {state.weather.cloud_cover_percent:.0f}%")
    else:
        print("Keine Wetterdaten verfügbar")
    print()

    print("--- SONSTIGES ---")
    print(f"Wochenende: {'Ja' if state.is_weekend else 'Nein'}")
    print(f"Feiertag: {'Ja - ' + state.holiday_name if state.is_holiday else 'Nein'}")
    print()

    print("--- ATMOSPHÄRE ---")
    print(state.get_atmosphere_description())
    print()

    print("--- STIMMUNGSMODIFIKATOREN ---")
    modifiers = sync.get_mood_modifiers()
    for key, value in modifiers.items():
        print(f"  {key}: {value:+.2f}")

    await sync.close()


if __name__ == "__main__":
    asyncio.run(main())
