from pydantic import BaseModel
from typing import Optional

# =========================================================================== #
#  TIC
# =========================================================================== #
class TAC(BaseModel):
    k: int
    n: int
    timestamp: int

# =========================================================================== #
#  TIC
# =========================================================================== #
class TIC(BaseModel):
    k: int
    timestamp: int
    pvPlannedDown: bool
    stgPlannedDown: bool
    allPlannedDown: bool

# =========================================================================== #
#  MeasuredWeather
# =========================================================================== #
class MeasuredWeather(BaseModel):
    rad_ar: float
    temp_ar: float
    wind_ar: float
    timestamp: int
    storeTimestamp: Optional[int] = None

# =========================================================================== #
#  MeasuredWeatherTIC
# =========================================================================== #
class MeasuredWeatherTIC(BaseModel):
    k: int
    rad_ar: float
    temp_ar: float
    wind_ar: float
    measuredTimestamp: int
    storeTimestamp: Optional[int] = None

# =========================================================================== #
#  OptimizationParameter
# =========================================================================== #
class OptimizationParameter(BaseModel):
    name: str
    value: float
    unit: str

# =========================================================================== #
#  SAMParameter
# =========================================================================== #
class SAMParameter(BaseModel):
    name: str
    value: float
    unit: str

# =========================================================================== #
#  ReceivedForecast
# =========================================================================== #
class ReceivedForecast(BaseModel):
    timestamp: int
    rad_ar: float
    temp_ar: float
    wind_ar: float
    storeTimestamp: float

# =========================================================================== #
#  SpotEstimatedTIC
# =========================================================================== #
class SpotEstimatedTIC(BaseModel):
    k: int
    spotMwhEUR: float
    estimationK: int

# =========================================================================== #
#  SpotPublishedTIC
# =========================================================================== #
class SpotPublishedTIC(BaseModel):
    k: int
    spotMwhEUR: float
    acceptedProgramKwh: float
    publishK: int

# =========================================================================== #
#  WeatherEstimateTAC
# =========================================================================== #
class WeatherEstimateTAC(BaseModel):
    k: int
    n: int
    rad_ar: float
    wind_ar: float
    temp_ar: int
    storeTimestamp: int
    forecastStoreTimestamp: int

# =========================================================================== #
#  WeatherEstimateTIC
# =========================================================================== #
class WeatherEstimateTIC(BaseModel):
    k: int
    rad_ar: float
    wind_ar: float
    temp_ar: int
    storeTimestamp: int
    forecastStoreTimestamp: int