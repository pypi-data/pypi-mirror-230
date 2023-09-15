"""This module provides the aliases of the output variables of all available models.

This file was automatically created by function |write_sequencealiases|.
"""

# import...
# ...from standard library
from typing import TYPE_CHECKING

# ...from HydPy
from hydpy.core.aliastools import LazyInOutSequenceImport

if TYPE_CHECKING:
    from hydpy.models.arma.arma_fluxes import QIn as arma_QIn
    from hydpy.models.arma.arma_fluxes import QOut as arma_QOut
    from hydpy.models.conv.conv_fluxes import ActualConstant as conv_ActualConstant
    from hydpy.models.conv.conv_fluxes import ActualFactor as conv_ActualFactor
    from hydpy.models.dam.dam_factors import WaterLevel as dam_WaterLevel
    from hydpy.models.dam.dam_fluxes import (
        AdjustedPrecipitation as dam_AdjustedPrecipitation,
    )
    from hydpy.models.dam.dam_fluxes import (
        AdjustedEvaporation as dam_AdjustedEvaporation,
    )
    from hydpy.models.dam.dam_fluxes import ActualEvaporation as dam_ActualEvaporation
    from hydpy.models.dam.dam_fluxes import Inflow as dam_Inflow
    from hydpy.models.dam.dam_fluxes import Exchange as dam_Exchange
    from hydpy.models.dam.dam_fluxes import (
        TotalRemoteDischarge as dam_TotalRemoteDischarge,
    )
    from hydpy.models.dam.dam_fluxes import (
        NaturalRemoteDischarge as dam_NaturalRemoteDischarge,
    )
    from hydpy.models.dam.dam_fluxes import RemoteDemand as dam_RemoteDemand
    from hydpy.models.dam.dam_fluxes import RemoteFailure as dam_RemoteFailure
    from hydpy.models.dam.dam_fluxes import (
        RequiredRemoteRelease as dam_RequiredRemoteRelease,
    )
    from hydpy.models.dam.dam_fluxes import (
        AllowedRemoteRelief as dam_AllowedRemoteRelief,
    )
    from hydpy.models.dam.dam_fluxes import (
        RequiredRemoteSupply as dam_RequiredRemoteSupply,
    )
    from hydpy.models.dam.dam_fluxes import (
        PossibleRemoteRelief as dam_PossibleRemoteRelief,
    )
    from hydpy.models.dam.dam_fluxes import ActualRemoteRelief as dam_ActualRemoteRelief
    from hydpy.models.dam.dam_fluxes import RequiredRelease as dam_RequiredRelease
    from hydpy.models.dam.dam_fluxes import TargetedRelease as dam_TargetedRelease
    from hydpy.models.dam.dam_fluxes import ActualRelease as dam_ActualRelease
    from hydpy.models.dam.dam_fluxes import (
        MissingRemoteRelease as dam_MissingRemoteRelease,
    )
    from hydpy.models.dam.dam_fluxes import (
        ActualRemoteRelease as dam_ActualRemoteRelease,
    )
    from hydpy.models.dam.dam_fluxes import FloodDischarge as dam_FloodDischarge
    from hydpy.models.dam.dam_fluxes import Outflow as dam_Outflow
    from hydpy.models.dam.dam_states import WaterVolume as dam_WaterVolume
    from hydpy.models.dummy.dummy_fluxes import Q as dummy_Q
    from hydpy.models.evap.evap_factors import (
        AdjustedWindSpeed as evap_AdjustedWindSpeed,
    )
    from hydpy.models.evap.evap_factors import (
        SaturationVapourPressure as evap_SaturationVapourPressure,
    )
    from hydpy.models.evap.evap_factors import (
        SaturationVapourPressureSlope as evap_SaturationVapourPressureSlope,
    )
    from hydpy.models.evap.evap_factors import (
        ActualVapourPressure as evap_ActualVapourPressure,
    )
    from hydpy.models.evap.evap_factors import (
        PsychrometricConstant as evap_PsychrometricConstant,
    )
    from hydpy.models.evap.evap_fluxes import (
        NetShortwaveRadiation as evap_NetShortwaveRadiation,
    )
    from hydpy.models.evap.evap_fluxes import (
        NetLongwaveRadiation as evap_NetLongwaveRadiation,
    )
    from hydpy.models.evap.evap_fluxes import NetRadiation as evap_NetRadiation
    from hydpy.models.evap.evap_fluxes import SoilHeatFlux as evap_SoilHeatFlux
    from hydpy.models.evap.evap_fluxes import (
        ReferenceEvapotranspiration as evap_ReferenceEvapotranspiration,
    )
    from hydpy.models.exch.exch_factors import DeltaWaterLevel as exch_DeltaWaterLevel
    from hydpy.models.exch.exch_fluxes import (
        PotentialExchange as exch_PotentialExchange,
    )
    from hydpy.models.exch.exch_fluxes import ActualExchange as exch_ActualExchange
    from hydpy.models.hbranch.hbranch_fluxes import (
        OriginalInput as hbranch_OriginalInput,
    )
    from hydpy.models.hbranch.hbranch_fluxes import (
        AdjustedInput as hbranch_AdjustedInput,
    )
    from hydpy.models.hland.hland_factors import TMean as hland_TMean
    from hydpy.models.hland.hland_factors import ContriArea as hland_ContriArea
    from hydpy.models.hland.hland_fluxes import InUZ as hland_InUZ
    from hydpy.models.hland.hland_fluxes import Perc as hland_Perc
    from hydpy.models.hland.hland_fluxes import Q0 as hland_Q0
    from hydpy.models.hland.hland_fluxes import Q1 as hland_Q1
    from hydpy.models.hland.hland_fluxes import GR2 as hland_GR2
    from hydpy.models.hland.hland_fluxes import RG2 as hland_RG2
    from hydpy.models.hland.hland_fluxes import GR3 as hland_GR3
    from hydpy.models.hland.hland_fluxes import RG3 as hland_RG3
    from hydpy.models.hland.hland_fluxes import InUH as hland_InUH
    from hydpy.models.hland.hland_fluxes import OutUH as hland_OutUH
    from hydpy.models.hland.hland_fluxes import RO as hland_RO
    from hydpy.models.hland.hland_fluxes import RA as hland_RA
    from hydpy.models.hland.hland_fluxes import RT as hland_RT
    from hydpy.models.hland.hland_fluxes import QT as hland_QT
    from hydpy.models.hland.hland_states import UZ as hland_UZ
    from hydpy.models.hland.hland_states import LZ as hland_LZ
    from hydpy.models.hland.hland_states import SG2 as hland_SG2
    from hydpy.models.hland.hland_states import SG3 as hland_SG3
    from hydpy.models.llake.llake_fluxes import QZ as llake_QZ
    from hydpy.models.llake.llake_fluxes import QA as llake_QA
    from hydpy.models.llake.llake_states import V as llake_V
    from hydpy.models.llake.llake_states import W as llake_W
    from hydpy.models.lland.lland_fluxes import QZ as lland_QZ
    from hydpy.models.lland.lland_fluxes import QZH as lland_QZH
    from hydpy.models.lland.lland_fluxes import TemLTag as lland_TemLTag
    from hydpy.models.lland.lland_fluxes import (
        DailyRelativeHumidity as lland_DailyRelativeHumidity,
    )
    from hydpy.models.lland.lland_fluxes import (
        DailySunshineDuration as lland_DailySunshineDuration,
    )
    from hydpy.models.lland.lland_fluxes import (
        DailyPossibleSunshineDuration as lland_DailyPossibleSunshineDuration,
    )
    from hydpy.models.lland.lland_fluxes import (
        DailyGlobalRadiation as lland_DailyGlobalRadiation,
    )
    from hydpy.models.lland.lland_fluxes import WindSpeed2m as lland_WindSpeed2m
    from hydpy.models.lland.lland_fluxes import (
        DailyWindSpeed2m as lland_DailyWindSpeed2m,
    )
    from hydpy.models.lland.lland_fluxes import WindSpeed10m as lland_WindSpeed10m
    from hydpy.models.lland.lland_fluxes import QDGZ as lland_QDGZ
    from hydpy.models.lland.lland_fluxes import QAH as lland_QAH
    from hydpy.models.lland.lland_fluxes import QA as lland_QA
    from hydpy.models.lland.lland_states import QDGZ1 as lland_QDGZ1
    from hydpy.models.lland.lland_states import QDGZ2 as lland_QDGZ2
    from hydpy.models.lland.lland_states import QIGZ1 as lland_QIGZ1
    from hydpy.models.lland.lland_states import QIGZ2 as lland_QIGZ2
    from hydpy.models.lland.lland_states import QBGZ as lland_QBGZ
    from hydpy.models.lland.lland_states import QDGA1 as lland_QDGA1
    from hydpy.models.lland.lland_states import QDGA2 as lland_QDGA2
    from hydpy.models.lland.lland_states import QIGA1 as lland_QIGA1
    from hydpy.models.lland.lland_states import QIGA2 as lland_QIGA2
    from hydpy.models.lland.lland_states import QBGA as lland_QBGA
    from hydpy.models.lstream.lstream_fluxes import QZ as lstream_QZ
    from hydpy.models.lstream.lstream_fluxes import QZA as lstream_QZA
    from hydpy.models.lstream.lstream_fluxes import QA as lstream_QA
    from hydpy.models.meteo.meteo_factors import (
        EarthSunDistance as meteo_EarthSunDistance,
    )
    from hydpy.models.meteo.meteo_factors import (
        SolarDeclination as meteo_SolarDeclination,
    )
    from hydpy.models.meteo.meteo_factors import (
        SunsetHourAngle as meteo_SunsetHourAngle,
    )
    from hydpy.models.meteo.meteo_factors import SolarTimeAngle as meteo_SolarTimeAngle
    from hydpy.models.meteo.meteo_factors import TimeOfSunrise as meteo_TimeOfSunrise
    from hydpy.models.meteo.meteo_factors import TimeOfSunset as meteo_TimeOfSunset
    from hydpy.models.meteo.meteo_factors import (
        PossibleSunshineDuration as meteo_PossibleSunshineDuration,
    )
    from hydpy.models.meteo.meteo_factors import (
        DailyPossibleSunshineDuration as meteo_DailyPossibleSunshineDuration,
    )
    from hydpy.models.meteo.meteo_factors import (
        UnadjustedSunshineDuration as meteo_UnadjustedSunshineDuration,
    )
    from hydpy.models.meteo.meteo_factors import (
        SunshineDuration as meteo_SunshineDuration,
    )
    from hydpy.models.meteo.meteo_factors import (
        DailySunshineDuration as meteo_DailySunshineDuration,
    )
    from hydpy.models.meteo.meteo_factors import (
        PortionDailyRadiation as meteo_PortionDailyRadiation,
    )
    from hydpy.models.meteo.meteo_fluxes import (
        ExtraterrestrialRadiation as meteo_ExtraterrestrialRadiation,
    )
    from hydpy.models.meteo.meteo_fluxes import (
        ClearSkySolarRadiation as meteo_ClearSkySolarRadiation,
    )
    from hydpy.models.meteo.meteo_fluxes import (
        UnadjustedGlobalRadiation as meteo_UnadjustedGlobalRadiation,
    )
    from hydpy.models.meteo.meteo_fluxes import (
        DailyGlobalRadiation as meteo_DailyGlobalRadiation,
    )
    from hydpy.models.meteo.meteo_fluxes import GlobalRadiation as meteo_GlobalRadiation
    from hydpy.models.musk.musk_fluxes import Inflow as musk_Inflow
    from hydpy.models.musk.musk_fluxes import Outflow as musk_Outflow
    from hydpy.models.test.test_fluxes import Q as test_Q
    from hydpy.models.test.test_states import S as test_S
    from hydpy.models.wland.wland_fluxes import PC as wland_PC
    from hydpy.models.wland.wland_fluxes import PES as wland_PES
    from hydpy.models.wland.wland_fluxes import PS as wland_PS
    from hydpy.models.wland.wland_fluxes import PV as wland_PV
    from hydpy.models.wland.wland_fluxes import PQ as wland_PQ
    from hydpy.models.wland.wland_fluxes import ETV as wland_ETV
    from hydpy.models.wland.wland_fluxes import ES as wland_ES
    from hydpy.models.wland.wland_fluxes import ET as wland_ET
    from hydpy.models.wland.wland_fluxes import FXS as wland_FXS
    from hydpy.models.wland.wland_fluxes import FXG as wland_FXG
    from hydpy.models.wland.wland_fluxes import CDG as wland_CDG
    from hydpy.models.wland.wland_fluxes import FGS as wland_FGS
    from hydpy.models.wland.wland_fluxes import FQS as wland_FQS
    from hydpy.models.wland.wland_fluxes import RH as wland_RH
    from hydpy.models.wland.wland_fluxes import R as wland_R
    from hydpy.models.wland.wland_states import DV as wland_DV
    from hydpy.models.wland.wland_states import DG as wland_DG
    from hydpy.models.wland.wland_states import HQ as wland_HQ
    from hydpy.models.wland.wland_states import HS as wland_HS
else:
    arma_QIn = LazyInOutSequenceImport(
        modulename="hydpy.models.arma.arma_fluxes",
        classname="QIn",
        alias="arma_QIn",
        namespace=locals(),
    )
    arma_QOut = LazyInOutSequenceImport(
        modulename="hydpy.models.arma.arma_fluxes",
        classname="QOut",
        alias="arma_QOut",
        namespace=locals(),
    )
    conv_ActualConstant = LazyInOutSequenceImport(
        modulename="hydpy.models.conv.conv_fluxes",
        classname="ActualConstant",
        alias="conv_ActualConstant",
        namespace=locals(),
    )
    conv_ActualFactor = LazyInOutSequenceImport(
        modulename="hydpy.models.conv.conv_fluxes",
        classname="ActualFactor",
        alias="conv_ActualFactor",
        namespace=locals(),
    )
    dam_WaterLevel = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_factors",
        classname="WaterLevel",
        alias="dam_WaterLevel",
        namespace=locals(),
    )
    dam_AdjustedPrecipitation = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="AdjustedPrecipitation",
        alias="dam_AdjustedPrecipitation",
        namespace=locals(),
    )
    dam_AdjustedEvaporation = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="AdjustedEvaporation",
        alias="dam_AdjustedEvaporation",
        namespace=locals(),
    )
    dam_ActualEvaporation = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="ActualEvaporation",
        alias="dam_ActualEvaporation",
        namespace=locals(),
    )
    dam_Inflow = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="Inflow",
        alias="dam_Inflow",
        namespace=locals(),
    )
    dam_Exchange = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="Exchange",
        alias="dam_Exchange",
        namespace=locals(),
    )
    dam_TotalRemoteDischarge = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="TotalRemoteDischarge",
        alias="dam_TotalRemoteDischarge",
        namespace=locals(),
    )
    dam_NaturalRemoteDischarge = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="NaturalRemoteDischarge",
        alias="dam_NaturalRemoteDischarge",
        namespace=locals(),
    )
    dam_RemoteDemand = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="RemoteDemand",
        alias="dam_RemoteDemand",
        namespace=locals(),
    )
    dam_RemoteFailure = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="RemoteFailure",
        alias="dam_RemoteFailure",
        namespace=locals(),
    )
    dam_RequiredRemoteRelease = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="RequiredRemoteRelease",
        alias="dam_RequiredRemoteRelease",
        namespace=locals(),
    )
    dam_AllowedRemoteRelief = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="AllowedRemoteRelief",
        alias="dam_AllowedRemoteRelief",
        namespace=locals(),
    )
    dam_RequiredRemoteSupply = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="RequiredRemoteSupply",
        alias="dam_RequiredRemoteSupply",
        namespace=locals(),
    )
    dam_PossibleRemoteRelief = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="PossibleRemoteRelief",
        alias="dam_PossibleRemoteRelief",
        namespace=locals(),
    )
    dam_ActualRemoteRelief = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="ActualRemoteRelief",
        alias="dam_ActualRemoteRelief",
        namespace=locals(),
    )
    dam_RequiredRelease = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="RequiredRelease",
        alias="dam_RequiredRelease",
        namespace=locals(),
    )
    dam_TargetedRelease = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="TargetedRelease",
        alias="dam_TargetedRelease",
        namespace=locals(),
    )
    dam_ActualRelease = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="ActualRelease",
        alias="dam_ActualRelease",
        namespace=locals(),
    )
    dam_MissingRemoteRelease = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="MissingRemoteRelease",
        alias="dam_MissingRemoteRelease",
        namespace=locals(),
    )
    dam_ActualRemoteRelease = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="ActualRemoteRelease",
        alias="dam_ActualRemoteRelease",
        namespace=locals(),
    )
    dam_FloodDischarge = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="FloodDischarge",
        alias="dam_FloodDischarge",
        namespace=locals(),
    )
    dam_Outflow = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_fluxes",
        classname="Outflow",
        alias="dam_Outflow",
        namespace=locals(),
    )
    dam_WaterVolume = LazyInOutSequenceImport(
        modulename="hydpy.models.dam.dam_states",
        classname="WaterVolume",
        alias="dam_WaterVolume",
        namespace=locals(),
    )
    dummy_Q = LazyInOutSequenceImport(
        modulename="hydpy.models.dummy.dummy_fluxes",
        classname="Q",
        alias="dummy_Q",
        namespace=locals(),
    )
    evap_AdjustedWindSpeed = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_factors",
        classname="AdjustedWindSpeed",
        alias="evap_AdjustedWindSpeed",
        namespace=locals(),
    )
    evap_SaturationVapourPressure = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_factors",
        classname="SaturationVapourPressure",
        alias="evap_SaturationVapourPressure",
        namespace=locals(),
    )
    evap_SaturationVapourPressureSlope = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_factors",
        classname="SaturationVapourPressureSlope",
        alias="evap_SaturationVapourPressureSlope",
        namespace=locals(),
    )
    evap_ActualVapourPressure = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_factors",
        classname="ActualVapourPressure",
        alias="evap_ActualVapourPressure",
        namespace=locals(),
    )
    evap_PsychrometricConstant = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_factors",
        classname="PsychrometricConstant",
        alias="evap_PsychrometricConstant",
        namespace=locals(),
    )
    evap_NetShortwaveRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_fluxes",
        classname="NetShortwaveRadiation",
        alias="evap_NetShortwaveRadiation",
        namespace=locals(),
    )
    evap_NetLongwaveRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_fluxes",
        classname="NetLongwaveRadiation",
        alias="evap_NetLongwaveRadiation",
        namespace=locals(),
    )
    evap_NetRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_fluxes",
        classname="NetRadiation",
        alias="evap_NetRadiation",
        namespace=locals(),
    )
    evap_SoilHeatFlux = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_fluxes",
        classname="SoilHeatFlux",
        alias="evap_SoilHeatFlux",
        namespace=locals(),
    )
    evap_ReferenceEvapotranspiration = LazyInOutSequenceImport(
        modulename="hydpy.models.evap.evap_fluxes",
        classname="ReferenceEvapotranspiration",
        alias="evap_ReferenceEvapotranspiration",
        namespace=locals(),
    )
    exch_DeltaWaterLevel = LazyInOutSequenceImport(
        modulename="hydpy.models.exch.exch_factors",
        classname="DeltaWaterLevel",
        alias="exch_DeltaWaterLevel",
        namespace=locals(),
    )
    exch_PotentialExchange = LazyInOutSequenceImport(
        modulename="hydpy.models.exch.exch_fluxes",
        classname="PotentialExchange",
        alias="exch_PotentialExchange",
        namespace=locals(),
    )
    exch_ActualExchange = LazyInOutSequenceImport(
        modulename="hydpy.models.exch.exch_fluxes",
        classname="ActualExchange",
        alias="exch_ActualExchange",
        namespace=locals(),
    )
    hbranch_OriginalInput = LazyInOutSequenceImport(
        modulename="hydpy.models.hbranch.hbranch_fluxes",
        classname="OriginalInput",
        alias="hbranch_OriginalInput",
        namespace=locals(),
    )
    hbranch_AdjustedInput = LazyInOutSequenceImport(
        modulename="hydpy.models.hbranch.hbranch_fluxes",
        classname="AdjustedInput",
        alias="hbranch_AdjustedInput",
        namespace=locals(),
    )
    hland_TMean = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_factors",
        classname="TMean",
        alias="hland_TMean",
        namespace=locals(),
    )
    hland_ContriArea = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_factors",
        classname="ContriArea",
        alias="hland_ContriArea",
        namespace=locals(),
    )
    hland_InUZ = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="InUZ",
        alias="hland_InUZ",
        namespace=locals(),
    )
    hland_Perc = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="Perc",
        alias="hland_Perc",
        namespace=locals(),
    )
    hland_Q0 = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="Q0",
        alias="hland_Q0",
        namespace=locals(),
    )
    hland_Q1 = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="Q1",
        alias="hland_Q1",
        namespace=locals(),
    )
    hland_GR2 = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="GR2",
        alias="hland_GR2",
        namespace=locals(),
    )
    hland_RG2 = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="RG2",
        alias="hland_RG2",
        namespace=locals(),
    )
    hland_GR3 = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="GR3",
        alias="hland_GR3",
        namespace=locals(),
    )
    hland_RG3 = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="RG3",
        alias="hland_RG3",
        namespace=locals(),
    )
    hland_InUH = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="InUH",
        alias="hland_InUH",
        namespace=locals(),
    )
    hland_OutUH = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="OutUH",
        alias="hland_OutUH",
        namespace=locals(),
    )
    hland_RO = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="RO",
        alias="hland_RO",
        namespace=locals(),
    )
    hland_RA = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="RA",
        alias="hland_RA",
        namespace=locals(),
    )
    hland_RT = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="RT",
        alias="hland_RT",
        namespace=locals(),
    )
    hland_QT = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_fluxes",
        classname="QT",
        alias="hland_QT",
        namespace=locals(),
    )
    hland_UZ = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_states",
        classname="UZ",
        alias="hland_UZ",
        namespace=locals(),
    )
    hland_LZ = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_states",
        classname="LZ",
        alias="hland_LZ",
        namespace=locals(),
    )
    hland_SG2 = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_states",
        classname="SG2",
        alias="hland_SG2",
        namespace=locals(),
    )
    hland_SG3 = LazyInOutSequenceImport(
        modulename="hydpy.models.hland.hland_states",
        classname="SG3",
        alias="hland_SG3",
        namespace=locals(),
    )
    llake_QZ = LazyInOutSequenceImport(
        modulename="hydpy.models.llake.llake_fluxes",
        classname="QZ",
        alias="llake_QZ",
        namespace=locals(),
    )
    llake_QA = LazyInOutSequenceImport(
        modulename="hydpy.models.llake.llake_fluxes",
        classname="QA",
        alias="llake_QA",
        namespace=locals(),
    )
    llake_V = LazyInOutSequenceImport(
        modulename="hydpy.models.llake.llake_states",
        classname="V",
        alias="llake_V",
        namespace=locals(),
    )
    llake_W = LazyInOutSequenceImport(
        modulename="hydpy.models.llake.llake_states",
        classname="W",
        alias="llake_W",
        namespace=locals(),
    )
    lland_QZ = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="QZ",
        alias="lland_QZ",
        namespace=locals(),
    )
    lland_QZH = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="QZH",
        alias="lland_QZH",
        namespace=locals(),
    )
    lland_TemLTag = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="TemLTag",
        alias="lland_TemLTag",
        namespace=locals(),
    )
    lland_DailyRelativeHumidity = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="DailyRelativeHumidity",
        alias="lland_DailyRelativeHumidity",
        namespace=locals(),
    )
    lland_DailySunshineDuration = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="DailySunshineDuration",
        alias="lland_DailySunshineDuration",
        namespace=locals(),
    )
    lland_DailyPossibleSunshineDuration = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="DailyPossibleSunshineDuration",
        alias="lland_DailyPossibleSunshineDuration",
        namespace=locals(),
    )
    lland_DailyGlobalRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="DailyGlobalRadiation",
        alias="lland_DailyGlobalRadiation",
        namespace=locals(),
    )
    lland_WindSpeed2m = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="WindSpeed2m",
        alias="lland_WindSpeed2m",
        namespace=locals(),
    )
    lland_DailyWindSpeed2m = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="DailyWindSpeed2m",
        alias="lland_DailyWindSpeed2m",
        namespace=locals(),
    )
    lland_WindSpeed10m = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="WindSpeed10m",
        alias="lland_WindSpeed10m",
        namespace=locals(),
    )
    lland_QDGZ = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="QDGZ",
        alias="lland_QDGZ",
        namespace=locals(),
    )
    lland_QAH = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="QAH",
        alias="lland_QAH",
        namespace=locals(),
    )
    lland_QA = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_fluxes",
        classname="QA",
        alias="lland_QA",
        namespace=locals(),
    )
    lland_QDGZ1 = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QDGZ1",
        alias="lland_QDGZ1",
        namespace=locals(),
    )
    lland_QDGZ2 = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QDGZ2",
        alias="lland_QDGZ2",
        namespace=locals(),
    )
    lland_QIGZ1 = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QIGZ1",
        alias="lland_QIGZ1",
        namespace=locals(),
    )
    lland_QIGZ2 = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QIGZ2",
        alias="lland_QIGZ2",
        namespace=locals(),
    )
    lland_QBGZ = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QBGZ",
        alias="lland_QBGZ",
        namespace=locals(),
    )
    lland_QDGA1 = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QDGA1",
        alias="lland_QDGA1",
        namespace=locals(),
    )
    lland_QDGA2 = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QDGA2",
        alias="lland_QDGA2",
        namespace=locals(),
    )
    lland_QIGA1 = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QIGA1",
        alias="lland_QIGA1",
        namespace=locals(),
    )
    lland_QIGA2 = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QIGA2",
        alias="lland_QIGA2",
        namespace=locals(),
    )
    lland_QBGA = LazyInOutSequenceImport(
        modulename="hydpy.models.lland.lland_states",
        classname="QBGA",
        alias="lland_QBGA",
        namespace=locals(),
    )
    lstream_QZ = LazyInOutSequenceImport(
        modulename="hydpy.models.lstream.lstream_fluxes",
        classname="QZ",
        alias="lstream_QZ",
        namespace=locals(),
    )
    lstream_QZA = LazyInOutSequenceImport(
        modulename="hydpy.models.lstream.lstream_fluxes",
        classname="QZA",
        alias="lstream_QZA",
        namespace=locals(),
    )
    lstream_QA = LazyInOutSequenceImport(
        modulename="hydpy.models.lstream.lstream_fluxes",
        classname="QA",
        alias="lstream_QA",
        namespace=locals(),
    )
    meteo_EarthSunDistance = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="EarthSunDistance",
        alias="meteo_EarthSunDistance",
        namespace=locals(),
    )
    meteo_SolarDeclination = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="SolarDeclination",
        alias="meteo_SolarDeclination",
        namespace=locals(),
    )
    meteo_SunsetHourAngle = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="SunsetHourAngle",
        alias="meteo_SunsetHourAngle",
        namespace=locals(),
    )
    meteo_SolarTimeAngle = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="SolarTimeAngle",
        alias="meteo_SolarTimeAngle",
        namespace=locals(),
    )
    meteo_TimeOfSunrise = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="TimeOfSunrise",
        alias="meteo_TimeOfSunrise",
        namespace=locals(),
    )
    meteo_TimeOfSunset = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="TimeOfSunset",
        alias="meteo_TimeOfSunset",
        namespace=locals(),
    )
    meteo_PossibleSunshineDuration = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="PossibleSunshineDuration",
        alias="meteo_PossibleSunshineDuration",
        namespace=locals(),
    )
    meteo_DailyPossibleSunshineDuration = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="DailyPossibleSunshineDuration",
        alias="meteo_DailyPossibleSunshineDuration",
        namespace=locals(),
    )
    meteo_UnadjustedSunshineDuration = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="UnadjustedSunshineDuration",
        alias="meteo_UnadjustedSunshineDuration",
        namespace=locals(),
    )
    meteo_SunshineDuration = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="SunshineDuration",
        alias="meteo_SunshineDuration",
        namespace=locals(),
    )
    meteo_DailySunshineDuration = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="DailySunshineDuration",
        alias="meteo_DailySunshineDuration",
        namespace=locals(),
    )
    meteo_PortionDailyRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_factors",
        classname="PortionDailyRadiation",
        alias="meteo_PortionDailyRadiation",
        namespace=locals(),
    )
    meteo_ExtraterrestrialRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_fluxes",
        classname="ExtraterrestrialRadiation",
        alias="meteo_ExtraterrestrialRadiation",
        namespace=locals(),
    )
    meteo_ClearSkySolarRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_fluxes",
        classname="ClearSkySolarRadiation",
        alias="meteo_ClearSkySolarRadiation",
        namespace=locals(),
    )
    meteo_UnadjustedGlobalRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_fluxes",
        classname="UnadjustedGlobalRadiation",
        alias="meteo_UnadjustedGlobalRadiation",
        namespace=locals(),
    )
    meteo_DailyGlobalRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_fluxes",
        classname="DailyGlobalRadiation",
        alias="meteo_DailyGlobalRadiation",
        namespace=locals(),
    )
    meteo_GlobalRadiation = LazyInOutSequenceImport(
        modulename="hydpy.models.meteo.meteo_fluxes",
        classname="GlobalRadiation",
        alias="meteo_GlobalRadiation",
        namespace=locals(),
    )
    musk_Inflow = LazyInOutSequenceImport(
        modulename="hydpy.models.musk.musk_fluxes",
        classname="Inflow",
        alias="musk_Inflow",
        namespace=locals(),
    )
    musk_Outflow = LazyInOutSequenceImport(
        modulename="hydpy.models.musk.musk_fluxes",
        classname="Outflow",
        alias="musk_Outflow",
        namespace=locals(),
    )
    test_Q = LazyInOutSequenceImport(
        modulename="hydpy.models.test.test_fluxes",
        classname="Q",
        alias="test_Q",
        namespace=locals(),
    )
    test_S = LazyInOutSequenceImport(
        modulename="hydpy.models.test.test_states",
        classname="S",
        alias="test_S",
        namespace=locals(),
    )
    wland_PC = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="PC",
        alias="wland_PC",
        namespace=locals(),
    )
    wland_PES = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="PES",
        alias="wland_PES",
        namespace=locals(),
    )
    wland_PS = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="PS",
        alias="wland_PS",
        namespace=locals(),
    )
    wland_PV = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="PV",
        alias="wland_PV",
        namespace=locals(),
    )
    wland_PQ = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="PQ",
        alias="wland_PQ",
        namespace=locals(),
    )
    wland_ETV = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="ETV",
        alias="wland_ETV",
        namespace=locals(),
    )
    wland_ES = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="ES",
        alias="wland_ES",
        namespace=locals(),
    )
    wland_ET = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="ET",
        alias="wland_ET",
        namespace=locals(),
    )
    wland_FXS = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="FXS",
        alias="wland_FXS",
        namespace=locals(),
    )
    wland_FXG = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="FXG",
        alias="wland_FXG",
        namespace=locals(),
    )
    wland_CDG = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="CDG",
        alias="wland_CDG",
        namespace=locals(),
    )
    wland_FGS = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="FGS",
        alias="wland_FGS",
        namespace=locals(),
    )
    wland_FQS = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="FQS",
        alias="wland_FQS",
        namespace=locals(),
    )
    wland_RH = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="RH",
        alias="wland_RH",
        namespace=locals(),
    )
    wland_R = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_fluxes",
        classname="R",
        alias="wland_R",
        namespace=locals(),
    )
    wland_DV = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_states",
        classname="DV",
        alias="wland_DV",
        namespace=locals(),
    )
    wland_DG = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_states",
        classname="DG",
        alias="wland_DG",
        namespace=locals(),
    )
    wland_HQ = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_states",
        classname="HQ",
        alias="wland_HQ",
        namespace=locals(),
    )
    wland_HS = LazyInOutSequenceImport(
        modulename="hydpy.models.wland.wland_states",
        classname="HS",
        alias="wland_HS",
        namespace=locals(),
    )

__all__ = [
    "arma_QIn",
    "arma_QOut",
    "conv_ActualConstant",
    "conv_ActualFactor",
    "dam_WaterLevel",
    "dam_AdjustedPrecipitation",
    "dam_AdjustedEvaporation",
    "dam_ActualEvaporation",
    "dam_Inflow",
    "dam_Exchange",
    "dam_TotalRemoteDischarge",
    "dam_NaturalRemoteDischarge",
    "dam_RemoteDemand",
    "dam_RemoteFailure",
    "dam_RequiredRemoteRelease",
    "dam_AllowedRemoteRelief",
    "dam_RequiredRemoteSupply",
    "dam_PossibleRemoteRelief",
    "dam_ActualRemoteRelief",
    "dam_RequiredRelease",
    "dam_TargetedRelease",
    "dam_ActualRelease",
    "dam_MissingRemoteRelease",
    "dam_ActualRemoteRelease",
    "dam_FloodDischarge",
    "dam_Outflow",
    "dam_WaterVolume",
    "dummy_Q",
    "evap_AdjustedWindSpeed",
    "evap_SaturationVapourPressure",
    "evap_SaturationVapourPressureSlope",
    "evap_ActualVapourPressure",
    "evap_PsychrometricConstant",
    "evap_NetShortwaveRadiation",
    "evap_NetLongwaveRadiation",
    "evap_NetRadiation",
    "evap_SoilHeatFlux",
    "evap_ReferenceEvapotranspiration",
    "exch_DeltaWaterLevel",
    "exch_PotentialExchange",
    "exch_ActualExchange",
    "hbranch_OriginalInput",
    "hbranch_AdjustedInput",
    "hland_TMean",
    "hland_ContriArea",
    "hland_InUZ",
    "hland_Perc",
    "hland_Q0",
    "hland_Q1",
    "hland_GR2",
    "hland_RG2",
    "hland_GR3",
    "hland_RG3",
    "hland_InUH",
    "hland_OutUH",
    "hland_RO",
    "hland_RA",
    "hland_RT",
    "hland_QT",
    "hland_UZ",
    "hland_LZ",
    "hland_SG2",
    "hland_SG3",
    "llake_QZ",
    "llake_QA",
    "llake_V",
    "llake_W",
    "lland_QZ",
    "lland_QZH",
    "lland_TemLTag",
    "lland_DailyRelativeHumidity",
    "lland_DailySunshineDuration",
    "lland_DailyPossibleSunshineDuration",
    "lland_DailyGlobalRadiation",
    "lland_WindSpeed2m",
    "lland_DailyWindSpeed2m",
    "lland_WindSpeed10m",
    "lland_QDGZ",
    "lland_QAH",
    "lland_QA",
    "lland_QDGZ1",
    "lland_QDGZ2",
    "lland_QIGZ1",
    "lland_QIGZ2",
    "lland_QBGZ",
    "lland_QDGA1",
    "lland_QDGA2",
    "lland_QIGA1",
    "lland_QIGA2",
    "lland_QBGA",
    "lstream_QZ",
    "lstream_QZA",
    "lstream_QA",
    "meteo_EarthSunDistance",
    "meteo_SolarDeclination",
    "meteo_SunsetHourAngle",
    "meteo_SolarTimeAngle",
    "meteo_TimeOfSunrise",
    "meteo_TimeOfSunset",
    "meteo_PossibleSunshineDuration",
    "meteo_DailyPossibleSunshineDuration",
    "meteo_UnadjustedSunshineDuration",
    "meteo_SunshineDuration",
    "meteo_DailySunshineDuration",
    "meteo_PortionDailyRadiation",
    "meteo_ExtraterrestrialRadiation",
    "meteo_ClearSkySolarRadiation",
    "meteo_UnadjustedGlobalRadiation",
    "meteo_DailyGlobalRadiation",
    "meteo_GlobalRadiation",
    "musk_Inflow",
    "musk_Outflow",
    "test_Q",
    "test_S",
    "wland_PC",
    "wland_PES",
    "wland_PS",
    "wland_PV",
    "wland_PQ",
    "wland_ETV",
    "wland_ES",
    "wland_ET",
    "wland_FXS",
    "wland_FXG",
    "wland_CDG",
    "wland_FGS",
    "wland_FQS",
    "wland_RH",
    "wland_R",
    "wland_DV",
    "wland_DG",
    "wland_HQ",
    "wland_HS",
]
