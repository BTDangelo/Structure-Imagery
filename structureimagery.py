from os import path
#also have seen import os.path but this way is faster
from datetime import datetime
#facilitates calculation of the amount of time taken for the 
import arcpy


def get_mxd(str_path_mxd, str_file_mxd):
    if path.isfile(str_path_mxd + "\\" + str_file_mxd):
        mxd = arcpy.mapping.MapDocument(str_path_mxd + "\\" + str_file_mxd)
    else:
        mxd = "can't find file " + str_file_mxd + " in folder " + str_path_mxd
    return mxd


def get_df(mxd_cur, str_df_name):
    df_got = arcpy.mapping.ListDataFrames(mxd_cur, str_df_name)[0]
    return df_got


def get_sel_layer(mxd_cur, str_poly, df_cur):
    lyr = arcpy.mapping.ListLayers(mxd_cur, str_poly, df_cur)[0]
    return lyr


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, field) as cursor:
        return sorted({row[0] for row in cursor})


def make_not_vis(df):
    for lyr in df:
        if lyr.isGroupLayer:
            for lyr_g in lyr.isGroupLayer:
                lyr_g.visible = False
        else:
            lyr.visible = False


def make_vis(mxd_cur, df, list_lyr):
    for str_lyr in list_lyr:
        lyr_cur = arcpy.mapping.ListLayers(mxd_cur, str_lyr, df)[0]
        lyr_cur.visible = True
        arcpy.Delete_management(lyr_cur)
    arcpy.RefreshTOC()
    arcpy.RefreshActiveView()


def make_sel(query, str_sel_lyr):
    lyr_temp_in = arcpy.CreateScratchName(workspace=arcpy.env.scratchGDB)
    lyr_temp_sel = arcpy.CreateScratchName(workspace=arcpy.env.scratchGDB)
    arcpy.MakeFeatureLayer_management(str_sel_lyr, lyr_temp_in)
    arcpy.Select_analysis(lyr_temp_sel, lyr_temp_in, query)
    return lyr_temp_sel


def gen_map_images(my_list, sel_lyr, df_zoom, mxd_cur, str_path_export, str_file_image_export_prefix):
    arcpy.env.overwriteOutput = True
    for curFID in my_list:
        query = '"FID" = {}'.format(curFID)
        str_new_lyr = make_sel(query, sel_lyr.dataSource)
        add_lyr = arcpy.mapping.Layer(str_new_lyr)
        arcpy.mapping.AddLayer(df_zoom, add_lyr, "TOP")
        df_zoom.panToExtent(add_lyr.getSelectedExtent())
        add_lyr.visible = True
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()
        arcpy.mapping.ExportToPNG(map_document=mxd_cur, out_png=str_path_export + '\\' + str_file_image_export_prefix + '{}'.format(curFID) + '_ext_pg.png')
        arcpy.mapping.RemoveLayer(df_zoom, add_lyr)
        arcpy.Delete_management(add_lyr)
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()
        del query, str_new_lyr, add_lyr
