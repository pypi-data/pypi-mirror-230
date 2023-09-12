
# Core Python imports.
import os
import sys

# Modify path so we can include the version of cruntils in this directory
# instead of relying on the user having it installed.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our package.
import cruntils

# EGM96 tests.
# NB. Please read notes on EGM implementation.
# Tests are performed against the sample values provided in the readme.txt
# that comes with the EGM96 geoid data. The original values are:
#
# Latitude     Longitude    Geoid Height metres
# 38.6281550,  269.7791550, -31.628
# -14.6212170, 305.0211140, -2.969
# 46.8743190,  102.4487290, -43.575
# -23.6174460, 133.8747120, 15.871
# 38.6254730,  359.9995000, 50.066
# -0.4667440,  0.0023000,   17.329
# Instanciate the egm object.
egm = cruntils.gis.Egm()

location = cruntils.gis.CLocation(38.6281550, 269.7791550, True, False)
assert egm.GetHeight(*location.GetLatLon(False)) == -31.61

location = cruntils.gis.CLocation(-14.6212170, 305.0211140, True, False)
assert egm.GetHeight(*location.GetLatLon(False)) == -2.97

location = cruntils.gis.CLocation(46.8743190, 102.4487290, True, False)
assert egm.GetHeight(*location.GetLatLon(False)) == -43.62

location = cruntils.gis.CLocation(-23.6174460, 133.8747120, True, False)
assert egm.GetHeight(*location.GetLatLon(False)) == 15.93

location = cruntils.gis.CLocation(38.6254730, 359.9995000, True, False)
assert egm.GetHeight(*location.GetLatLon(False)) == 50.04

location = cruntils.gis.CLocation(-0.4667440, 0.0023000, True, False)
assert egm.GetHeight(*location.GetLatLon(False)) == 17.34

# Location class testing.
location = cruntils.gis.CLocation(29.97914809004421, 31.13419577459987)
location.SetName("The Great Pyramid of Giza")
assert location.GetLat(True)  == 29.97914809004421
assert location.GetLat(False) == 119.97914809004421
assert location.GetLon(True)  == 31.13419577459987
assert location.GetLon(False) == 31.13419577459987
assert egm.GetHeight(*location.GetLatLon(False)) == 15.46

location = cruntils.gis.CLocation(13.412544924724, 103.866982081196)
assert location.GetLat(True)  == 13.412544924724
assert location.GetLat(False) == 103.412544924724
assert location.GetLon(True)  == 103.866982081196
assert location.GetLon(False) == 103.866982081196
assert egm.GetHeight(*location.GetLatLon(False)) == -20.74

location = cruntils.gis.CLocation(-33.856814228066426, 151.21527245566526)
assert location.GetLat(True)  == -33.856814228066426
assert location.GetLat(False) == 56.143185771933574
assert location.GetLon(True)  == 151.21527245566526
assert location.GetLon(False) == 151.21527245566526
assert egm.GetHeight(*location.GetLatLon(False)) == 22.46

location = cruntils.gis.CLocation(48.85824194192016, 2.2947293419960277)
assert location.GetLat(True)  == 48.85824194192016
assert location.GetLat(False) == 138.85824194192017
assert location.GetLon(True)  == 2.2947293419960277
assert location.GetLon(False) == 2.2947293419960277
assert egm.GetHeight(*location.GetLatLon(False)) == 44.58

location = cruntils.gis.CLocation(27.175082927193554, 78.04218888603889)
assert location.GetLat(True)  == 27.175082927193554
assert location.GetLat(False) == 117.17508292719356
assert location.GetLon(True)  == 78.04218888603889
assert location.GetLon(False) == 78.04218888603889
assert egm.GetHeight(*location.GetLatLon(False)) == -56.65

location = cruntils.gis.CLocation(25.197099645751745, 55.27436713304521)
assert location.GetLat(True)  == 25.197099645751745
assert location.GetLat(False) == 115.19709964575175
assert location.GetLon(True)  == 55.27436713304521
assert location.GetLon(False) == 55.27436713304521
assert egm.GetHeight(*location.GetLatLon(False)) == -33.72

location = cruntils.gis.CLocation(-13.16288083855811, -72.54499246486483)
assert location.GetLat(True)  == -13.16288083855811
assert location.GetLat(False) == 76.83711916144189
assert location.GetLon(True)  == -72.54499246486483
assert location.GetLon(False) == 287.45500753513517
assert egm.GetHeight(*location.GetLatLon(False)) == 41.0

location = cruntils.gis.CLocation(40.4328165861077, 116.56384082714345)
assert location.GetLat(True)  == 40.4328165861077
assert location.GetLat(False) == 130.4328165861077
assert location.GetLon(True)  == 116.56384082714345
assert location.GetLon(False) == 116.56384082714345
assert egm.GetHeight(*location.GetLatLon(False)) == -8.84

location = cruntils.gis.CLocation(43.87893406761528, -103.45910824083181)
assert location.GetLat(True)  == 43.87893406761528
assert location.GetLat(False) == 133.8789340676153
assert location.GetLon(True)  == -103.45910824083181
assert location.GetLon(False) == 256.54089175916819
assert egm.GetHeight(*location.GetLatLon(False)) == -14.34

location = cruntils.gis.CLocation(48.636040758988834, -1.5113842779991045)
assert location.GetLat(True)  == 48.636040758988834
assert location.GetLat(False) == 138.63604075898883
assert location.GetLon(True)  == -1.5113842779991045
assert location.GetLon(False) == 358.4886157220008955
assert egm.GetHeight(*location.GetLatLon(False)) == 48.63

location = cruntils.gis.CLocation(37.971715070563704, 23.72611403397619)
assert location.GetLat(True)  == 37.971715070563704
assert location.GetLat(False) == 127.9717150705637
assert location.GetLon(True)  == 23.72611403397619
assert location.GetLon(False) == 23.72611403397619
assert egm.GetHeight(*location.GetLatLon(False)) == 38.47

location = cruntils.gis.CLocation(52.51629349301016, 13.37766047582947)
assert location.GetLat(True)  == 52.51629349301016
assert location.GetLat(False) == 142.51629349301015
assert location.GetLon(True)  == 13.37766047582947
assert location.GetLon(False) == 13.37766047582947
assert egm.GetHeight(*location.GetLatLon(False)) == 39.57

location = cruntils.gis.CLocation(-27.122237695511924, -109.28847085908615)
assert location.GetLat(True)  == -27.122237695511924
assert location.GetLat(False) == 62.87776230448807
assert location.GetLon(True)  == -109.28847085908615
assert location.GetLon(False) == 250.71152914091385
assert egm.GetHeight(*location.GetLatLon(False)) == -5.02

location = cruntils.gis.CLocation(37.819967553225766, -122.47857851638965)
assert location.GetLat(True)  == 37.819967553225766
assert location.GetLat(False) == 127.81996755322577
assert location.GetLon(True)  == -122.47857851638965
assert location.GetLon(False) == 237.52142148361037
assert egm.GetHeight(*location.GetLatLon(False)) == -32.27

location = cruntils.gis.CLocation(47.55755543652021, 10.749872777217082)
assert location.GetLat(True)  == 47.55755543652021
assert location.GetLat(False) == 137.5575554365202
assert location.GetLon(True)  == 10.749872777217082
assert location.GetLon(False) == 10.749872777217082
assert egm.GetHeight(*location.GetLatLon(False)) == 47.57

location = cruntils.gis.CLocation(43.723008691837215, 10.39664187812666)
assert location.GetLat(True)  == 43.723008691837215
assert location.GetLat(False) == 133.7230086918372
assert location.GetLon(True)  == 10.39664187812666
assert location.GetLon(False) == 10.39664187812666
assert egm.GetHeight(*location.GetLatLon(False)) == 46.88

location = cruntils.gis.CLocation(-17.925536940892446, 25.8585721157442)
assert location.GetLat(True)  == -17.925536940892446
assert location.GetLat(False) == 72.07446305910756
assert location.GetLon(True)  == 25.8585721157442
assert location.GetLon(False) == 25.8585721157442
assert egm.GetHeight(*location.GetLatLon(False)) == 7.97

location = cruntils.gis.CLocation(31.776694243124926, 35.234550416303016)
assert location.GetLat(True)  == 31.776694243124926
assert location.GetLat(False) == 121.77669424312492
assert location.GetLon(True)  == 35.234550416303016
assert location.GetLon(False) == 35.234550416303016
assert egm.GetHeight(*location.GetLatLon(False)) == 20.17

location = cruntils.gis.CLocation(55.24079494341456, -6.511485424530822)
assert location.GetLat(True)  == 55.24079494341456
assert location.GetLat(False) == 145.24079494341456
assert location.GetLon(True)  == -6.511485424530822
assert location.GetLon(False) == 353.488514575469178
assert egm.GetHeight(*location.GetLatLon(False)) == 56.43

location = cruntils.gis.CLocation(51.50135039825405, -0.14187864274170406)
assert location.GetLat(True)  == 51.50135039825405
assert location.GetLat(False) == 141.50135039825403
assert location.GetLon(True)  == -0.14187864274170406
assert location.GetLon(False) == 359.85812135725829594
assert egm.GetHeight(*location.GetLatLon(False)) == 45.98

location = cruntils.gis.CLocation(41.40370129831798, 2.1744141615926087)
assert location.GetLat(True)  == 41.40370129831798
assert location.GetLat(False) == 131.40370129831797
assert location.GetLon(True)  == 2.1744141615926087
assert location.GetLon(False) == 2.1744141615926087
assert egm.GetHeight(*location.GetLatLon(False)) == 49.49

location = cruntils.gis.CLocation(-22.95238321031523, -43.210476226821186)
assert location.GetLat(True)  == -22.95238321031523
assert location.GetLat(False) == 67.04761678968477
assert location.GetLon(True)  == -43.210476226821186
assert location.GetLon(False) == 316.789523773178814
assert egm.GetHeight(*location.GetLatLon(False)) == -5.46

location = cruntils.gis.CLocation(41.00523488627207, 28.976971976352964)
assert location.GetLat(True)  == 41.00523488627207
assert location.GetLat(False) == 131.00523488627206
assert location.GetLon(True)  == 28.976971976352964
assert location.GetLon(False) == 28.976971976352964
assert egm.GetHeight(*location.GetLatLon(False)) == 37.41

location = cruntils.gis.CLocation(41.89020999827253, 12.492330841334322)
assert location.GetLat(True)  == 41.89020999827253
assert location.GetLat(False) == 131.89020999827252
assert location.GetLon(True)  == 12.492330841334322
assert location.GetLon(False) == 12.492330841334322
assert egm.GetHeight(*location.GetLatLon(False)) == 48.46

location = cruntils.gis.CLocation(13.749831620390959, 100.49158250207049)
assert location.GetLat(True)  == 13.749831620390959
assert location.GetLat(False) == 103.74983162039096
assert location.GetLon(True)  == 100.49158250207049
assert location.GetLon(False) == 100.49158250207049
assert egm.GetHeight(*location.GetLatLon(False)) == -31.64

location = cruntils.gis.CLocation(40.68930946193621, -74.04454141836152)
assert location.GetLat(True)  == 40.68930946193621
assert location.GetLat(False) == 130.6893094619362
assert location.GetLon(True)  == -74.04454141836152
assert location.GetLon(False) == 285.95545858163848
assert egm.GetHeight(*location.GetLatLon(False)) == -32.87

location = cruntils.gis.CLocation(30.328526247400003, 35.444262214033294)
assert location.GetLat(True)  == 30.328526247400003
assert location.GetLat(False) == 120.3285262474
assert location.GetLon(True)  == 35.444262214033294
assert location.GetLon(False) == 35.444262214033294
assert egm.GetHeight(*location.GetLatLon(False)) == 18.39

location = cruntils.gis.CLocation(20.83065925595387, 107.096572109152)
assert location.GetLat(True)  == 20.83065925595387
assert location.GetLat(False) == 110.83065925595386
assert location.GetLon(True)  == 107.096572109152
assert location.GetLon(False) == 107.096572109152
assert egm.GetHeight(*location.GetLatLon(False)) == -23.44

location = cruntils.gis.CLocation(51.17886977737434, -1.8261692863615964)
assert location.GetLat(True)  == 51.17886977737434
assert location.GetLat(False) == 141.17886977737433
assert location.GetLon(True)  == -1.8261692863615964
assert location.GetLon(False) == 358.1738307136384036
assert egm.GetHeight(*location.GetLatLon(False)) == 47.88

location = cruntils.gis.CLocation(36.46145193248103, 25.37561594083781)
assert location.GetLat(True)  == 36.46145193248103
assert location.GetLat(False) == 126.46145193248103
assert location.GetLon(True)  == 25.37561594083781
assert location.GetLon(False) == 25.37561594083781
assert egm.GetHeight(*location.GetLatLon(False)) == 34.88

location = cruntils.gis.CLocation(35.363020326680214, 138.72969579753973)
assert location.GetLat(True)  == 35.363020326680214
assert location.GetLat(False) == 125.36302032668021
assert location.GetLon(True)  == 138.72969579753973
assert location.GetLon(False) == 138.72969579753973
assert egm.GetHeight(*location.GetLatLon(False)) == 41.25

location = cruntils.gis.CLocation(29.656121190521272, 91.11770107604704)
assert location.GetLat(True)  == 29.656121190521272
assert location.GetLat(False) == 119.65612119052128
assert location.GetLon(True)  == 91.11770107604704
assert location.GetLon(False) == 91.11770107604704
assert egm.GetHeight(*location.GetLatLon(False)) == -34.66

# Test converting angles, signed / un-signed.
assert cruntils.utils.ConvertAngle(-180, False) == 180
assert cruntils.utils.ConvertAngle(-170, False) == 190
assert cruntils.utils.ConvertAngle(-160, False) == 200
assert cruntils.utils.ConvertAngle(-150, False) == 210
assert cruntils.utils.ConvertAngle(-140, False) == 220
assert cruntils.utils.ConvertAngle(-130, False) == 230
assert cruntils.utils.ConvertAngle(-120, False) == 240
assert cruntils.utils.ConvertAngle(-110, False) == 250
assert cruntils.utils.ConvertAngle(-100, False) == 260
assert cruntils.utils.ConvertAngle(-90, False)  == 270
assert cruntils.utils.ConvertAngle(-80, False)  == 280
assert cruntils.utils.ConvertAngle(-70, False)  == 290
assert cruntils.utils.ConvertAngle(-60, False)  == 300
assert cruntils.utils.ConvertAngle(-50, False)  == 310
assert cruntils.utils.ConvertAngle(-40, False)  == 320
assert cruntils.utils.ConvertAngle(-30, False)  == 330
assert cruntils.utils.ConvertAngle(-20, False)  == 340
assert cruntils.utils.ConvertAngle(-10, False)  == 350
assert cruntils.utils.ConvertAngle(-0, False)   == 0
assert cruntils.utils.ConvertAngle(0, False)    == 0
assert cruntils.utils.ConvertAngle(45, False)   == 45
assert cruntils.utils.ConvertAngle(90, False)   == 90
assert cruntils.utils.ConvertAngle(180, False)  == 180
assert cruntils.utils.ConvertAngle(270, False)  == 270
assert cruntils.utils.ConvertAngle(360, False)  == 0
assert cruntils.utils.ConvertAngle(400, False)  == 40

assert cruntils.utils.ConvertAngle(0, True)  == 0
assert cruntils.utils.ConvertAngle(10, True)  == 10
assert cruntils.utils.ConvertAngle(20, True)  == 20
assert cruntils.utils.ConvertAngle(30, True)  == 30
assert cruntils.utils.ConvertAngle(40, True)  == 40
assert cruntils.utils.ConvertAngle(50, True)  == 50
assert cruntils.utils.ConvertAngle(60, True)  == 60
assert cruntils.utils.ConvertAngle(70, True)  == 70
assert cruntils.utils.ConvertAngle(80, True)  == 80
assert cruntils.utils.ConvertAngle(90, True)  == 90
assert cruntils.utils.ConvertAngle(100, True)  == 100
assert cruntils.utils.ConvertAngle(110, True)  == 110
assert cruntils.utils.ConvertAngle(120, True)  == 120
assert cruntils.utils.ConvertAngle(130, True)  == 130
assert cruntils.utils.ConvertAngle(140, True)  == 140
assert cruntils.utils.ConvertAngle(150, True)  == 150
assert cruntils.utils.ConvertAngle(160, True)  == 160
assert cruntils.utils.ConvertAngle(170, True)  == 170
assert cruntils.utils.ConvertAngle(180, True)  == 180
assert cruntils.utils.ConvertAngle(190, True)  == -170
assert cruntils.utils.ConvertAngle(200, True)  == -160
assert cruntils.utils.ConvertAngle(210, True)  == -150
assert cruntils.utils.ConvertAngle(220, True)  == -140
assert cruntils.utils.ConvertAngle(230, True)  == -130
assert cruntils.utils.ConvertAngle(240, True)  == -120
assert cruntils.utils.ConvertAngle(250, True)  == -110
assert cruntils.utils.ConvertAngle(260, True)  == -100
assert cruntils.utils.ConvertAngle(270, True)  == -90
assert cruntils.utils.ConvertAngle(280, True)  == -80
assert cruntils.utils.ConvertAngle(290, True)  == -70
assert cruntils.utils.ConvertAngle(300, True)  == -60
assert cruntils.utils.ConvertAngle(310, True)  == -50
assert cruntils.utils.ConvertAngle(320, True)  == -40
assert cruntils.utils.ConvertAngle(330, True)  == -30
assert cruntils.utils.ConvertAngle(340, True)  == -20
assert cruntils.utils.ConvertAngle(350, True)  == -10
assert cruntils.utils.ConvertAngle(360, True)  == 0
assert cruntils.utils.ConvertAngle(370, True)  == 10
assert cruntils.utils.ConvertAngle(380, True)  == 20
assert cruntils.utils.ConvertAngle(390, True)  == 30
assert cruntils.utils.ConvertAngle(400, True)  == 40




# Define a list of trig pillar locations.
trig_pillar_locations_list = [
    { "name": "Outwood",        "grid_ref": "TQ 33246 45539", "wgs84_latlon": ["51 11 36.76 N", "000 05 40.22 W"]},
    { "name": "Chat Hill Farm", "grid_ref": "TQ 37978 48283" },
    { "name": "Gaywood Farm",   "grid_ref": "TQ 43190 48740" },
    { "name": "Mountjoy Farm",  "grid_ref": "TQ 51279 47834" },
    { "name": "Dry Hill",       "grid_ref": "TQ 43200 41606" },
    { "name": "Markbeech",      "grid_ref": "TQ 47758 42534" },
    { "name": "Smarts Hill",    "grid_ref": "TQ 51345 42253" },
    { "name": "Great Bounds",   "grid_ref": "TQ 57293 43566" },
    { "name": "Salehurst",      "grid_ref": "TQ 48431 39143" },
    { "name": "Cherry Garden",  "grid_ref": "TQ 51101 35644" },
    { "name": "Hindleap",       "grid_ref": "TQ 40354 32381" },
    { "name": "Gills Lap",      "grid_ref": "TQ 46859 31965" },
    { "name": "Crowborough",    "grid_ref": "TQ 51169 30761" }
]

# Need to do maths for grid to lat lon!