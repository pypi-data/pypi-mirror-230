from model_service.connection import ModelLaunchClient
from model_service.inference import ModelInferenceClient

# def generate_handler_example(param):
#     file_handler = open(param + "handler.py", 'w')
#     file_input = open(param + "input.json", 'w')
#
#     tmp = open("../example/handler.py", 'r').read()
#     print(tmp)
#
#     json = '''[
#   {
#     "field_a": 833.0,
#     "field_b": 27.0
#   },
#   {
#     "field_a": -28.0,
#     "field_b": -1.0
#   }
# ]
#     '''
#
#     file_handler.write(tmp)  # 写入内容信息
#     file_input.write(json)
#     file_handler.close()
#     file_input.close()
#     print('ok')


if __name__ == '__main__':
    """
        env: intranet/extranet 指定内/外网环境
        source_path: 本地模型文件路径
        model_name: 唯一模型名(建议可以使用 GitLab 指定的项目名)
    """
    client = ModelLaunchClient("http://ms.research-pro.sy.cvte.cn")
    #
    # client = ModelInferenceClient()
    # # generate_handler_example("./")
    #
    model_id = client.upload(env="extranet",
                             source_path="/Users/zsm/workspace/CVTE/bm/model-service-handler/en-rec-lgbm",
                             model_name="en_rec_lgbm")
    # # print(model_id)
    # model_id = "en_rec_lgbm_1694745874"
    # client.distribute(model_id=model_id, torchserve_id="ts-ex-cpu-1")
    print(client.launch(model_id=model_id, torchserve_id="ts-ex-cpu-1"))

    # client.package()
    # print(client.distribute(model_id=model_id, torchserve_id="ts-ex-cpu-1"))
    # print(client.final_launch())
    # # client.list_models()
    # # 打包、分发、上线
    # client.launch(model_id, "torchserve_id")
    # client.test()
    #
    json_str = '''[{"activate_date_day":6,"activate_date_day_diff":-461,"activate_date_dayofweek":4,"activate_date_dayofyear":96,"activate_date_month":4,"activate_date_month_diff":-16,"activate_date_quarter":2,"activate_date_weekday":3,"activate_date_weekofyear":14,"activate_date_workday":0,"activate_date_year":2023,"city":0,"coursegroup_study_count":60,"is_lecturer":0,"province":0,"register_date_day":16,"register_date_day_diff":290,"register_date_dayofweek":2,"register_date_dayofyear":75,"register_date_month":3,"register_date_month_diff":9,"register_date_quarter":1,"register_date_weekday":1,"register_date_weekofyear":11,"register_date_year":2021,"register_source":14,"user_15d_active":1,"user_15d_click_cnt":1,"user_15d_click_course_num":0,"user_15d_click_group_num":0,"user_15d_search_cnt":0,"user_1d_active":0,"user_1d_click_cnt":0,"user_1d_click_course_num":0,"user_1d_click_group_num":0,"user_1d_search_cnt":0,"user_30d_active":1,"user_30d_click_cnt":12,"user_30d_click_course_num":0,"user_30d_click_group_num":7,"user_30d_search_cnt":2,"user_3d_active":0,"user_3d_click_cnt":0,"user_3d_click_course_num":0,"user_3d_click_group_num":0,"user_3d_search_cnt":0,"user_7d_active":0,"user_7d_click_cnt":0,"user_7d_click_course_num":0,"user_7d_click_group_num":0,"user_7d_search_cnt":0,"user_stage":3,"user_subject":49,"cg_stage":3.0,"cg_subject":22.0,"cg_category":10.0,"lecturer_id":5683.0,"lecturer_name":586.0,"course_count":1.0,"quality":65.11894,"score":4.62609,"score_user_count":115.0,"play_count":2814.0,"study_cnt":1236.0,"study_rate":0.22168,"comment_num":112.0,"star":4.62609,"quality_category":1.0,"lecturer_register_source":24.0,"lecturer_province":25.0,"lecturer_city":40.0,"cg_1d_click_cnt":0.0,"cg_1d_click_user_num":0.0,"cg_1d_click_stage_num":0.0,"cg_1d_click_subject_num":0.0,"cg_1d_click_province_num":0.0,"cg_3d_click_cnt":0.0,"cg_3d_click_user_num":0.0,"cg_3d_click_stage_num":0.0,"cg_3d_click_subject_num":0.0,"cg_3d_click_province_num":0.0,"cg_7d_click_cnt":0.0,"cg_7d_click_user_num":0.0,"cg_7d_click_stage_num":0.0,"cg_7d_click_subject_num":0.0,"cg_7d_click_province_num":0.0,"cg_15d_click_cnt":0.0,"cg_15d_click_user_num":0.0,"cg_15d_click_stage_num":0.0,"cg_15d_click_subject_num":0.0,"cg_15d_click_province_num":0.0,"cg_30d_click_cnt":1.0,"cg_30d_click_user_num":1.0,"cg_30d_click_stage_num":1.0,"cg_30d_click_subject_num":1.0,"cg_30d_click_province_num":1.0,"study_num":1237.0,"dt_dayofweek":3.0,"dt_day":30.0,"dt_month":8.0,"dt_year":2023.0,"dt_dayofyear":242.0,"dt_weekofyear":35.0,"dt_quarter":3.0,"dt_weekday":2.0,"dt_day_diff":-607.0,"dt_month_diff":-20.0,"dt_workday":1.0,"lecturer_activate_date_dayofweek":7.0,"lecturer_activate_date_day":11.0,"lecturer_activate_date_month":9.0,"lecturer_activate_date_year":2016.0,"lecturer_activate_date_dayofyear":255.0,"lecturer_activate_date_weekofyear":36.0,"lecturer_activate_date_quarter":3.0,"lecturer_activate_date_weekday":6.0,"lecturer_activate_date_day_diff":1935.0,"lecturer_activate_date_month_diff":63.0,"lecturer_activate_date_workday":0.0,"lecturer_register_date_dayofweek":7.0,"lecturer_register_date_day":11.0,"lecturer_register_date_month":9.0,"lecturer_register_date_year":2016.0,"lecturer_register_date_dayofyear":255.0,"lecturer_register_date_weekofyear":36.0,"lecturer_register_date_quarter":3.0,"lecturer_register_date_weekday":6.0,"lecturer_register_date_day_diff":1935.0,"lecturer_register_date_month_diff":63.0,"publish_time_dayofweek":4.0,"publish_time_day":19.0,"publish_time_month":9.0,"publish_time_year":2019.0,"publish_time_dayofyear":262.0,"publish_time_weekofyear":38.0,"publish_time_quarter":3.0,"publish_time_weekday":3.0,"publish_time_day_diff":833.0,"publish_time_month_diff":27.0},{"activate_date_day":6,"activate_date_day_diff":-461,"activate_date_dayofweek":4,"activate_date_dayofyear":96,"activate_date_month":4,"activate_date_month_diff":-16,"activate_date_quarter":2,"activate_date_weekday":3,"activate_date_weekofyear":14,"activate_date_workday":0,"activate_date_year":2023,"city":0,"coursegroup_study_count":60,"is_lecturer":0,"province":0,"register_date_day":16,"register_date_day_diff":290,"register_date_dayofweek":2,"register_date_dayofyear":75,"register_date_month":3,"register_date_month_diff":9,"register_date_quarter":1,"register_date_weekday":1,"register_date_weekofyear":11,"register_date_year":2021,"register_source":14,"user_15d_active":1,"user_15d_click_cnt":1,"user_15d_click_course_num":0,"user_15d_click_group_num":0,"user_15d_search_cnt":0,"user_1d_active":0,"user_1d_click_cnt":0,"user_1d_click_course_num":0,"user_1d_click_group_num":0,"user_1d_search_cnt":0,"user_30d_active":1,"user_30d_click_cnt":12,"user_30d_click_course_num":0,"user_30d_click_group_num":7,"user_30d_search_cnt":2,"user_3d_active":0,"user_3d_click_cnt":0,"user_3d_click_course_num":0,"user_3d_click_group_num":0,"user_3d_search_cnt":0,"user_7d_active":0,"user_7d_click_cnt":0,"user_7d_click_course_num":0,"user_7d_click_group_num":0,"user_7d_search_cnt":0,"user_stage":3,"user_subject":49,"cg_stage":2.0,"cg_subject":22.0,"cg_category":10.0,"lecturer_id":930.0,"lecturer_name":1434.0,"course_count":1.0,"quality":66.43278,"score":4.80162,"score_user_count":247.0,"play_count":7459.0,"study_cnt":3624.0,"study_rate":0.25635,"comment_num":225.0,"star":4.80162,"quality_category":1.0,"lecturer_register_source":11.0,"lecturer_province":13.0,"lecturer_city":194.0,"cg_1d_click_cnt":0.0,"cg_1d_click_user_num":0.0,"cg_1d_click_stage_num":0.0,"cg_1d_click_subject_num":0.0,"cg_1d_click_province_num":0.0,"cg_3d_click_cnt":3.0,"cg_3d_click_user_num":3.0,"cg_3d_click_stage_num":3.0,"cg_3d_click_subject_num":3.0,"cg_3d_click_province_num":3.0,"cg_7d_click_cnt":11.0,"cg_7d_click_user_num":11.0,"cg_7d_click_stage_num":11.0,"cg_7d_click_subject_num":11.0,"cg_7d_click_province_num":11.0,"cg_15d_click_cnt":17.0,"cg_15d_click_user_num":17.0,"cg_15d_click_stage_num":17.0,"cg_15d_click_subject_num":17.0,"cg_15d_click_province_num":17.0,"cg_30d_click_cnt":33.0,"cg_30d_click_user_num":33.0,"cg_30d_click_stage_num":33.0,"cg_30d_click_subject_num":33.0,"cg_30d_click_province_num":33.0,"study_num":3625.0,"dt_dayofweek":3.0,"dt_day":30.0,"dt_month":8.0,"dt_year":2023.0,"dt_dayofyear":242.0,"dt_weekofyear":35.0,"dt_quarter":3.0,"dt_weekday":2.0,"dt_day_diff":-607.0,"dt_month_diff":-20.0,"dt_workday":1.0,"lecturer_activate_date_dayofweek":2.0,"lecturer_activate_date_day":12.0,"lecturer_activate_date_month":6.0,"lecturer_activate_date_year":2018.0,"lecturer_activate_date_dayofyear":163.0,"lecturer_activate_date_weekofyear":24.0,"lecturer_activate_date_quarter":2.0,"lecturer_activate_date_weekday":1.0,"lecturer_activate_date_day_diff":1297.0,"lecturer_activate_date_month_diff":42.0,"lecturer_activate_date_workday":0.0,"lecturer_register_date_dayofweek":1.0,"lecturer_register_date_day":21.0,"lecturer_register_date_month":5.0,"lecturer_register_date_year":2018.0,"lecturer_register_date_dayofyear":141.0,"lecturer_register_date_weekofyear":21.0,"lecturer_register_date_quarter":2.0,"lecturer_register_date_weekday":0.0,"lecturer_register_date_day_diff":1319.0,"lecturer_register_date_month_diff":43.0,"publish_time_dayofweek":5.0,"publish_time_day":28.0,"publish_time_month":1.0,"publish_time_year":2022.0,"publish_time_dayofyear":28.0,"publish_time_weekofyear":4.0,"publish_time_quarter":1.0,"publish_time_weekday":4.0,"publish_time_day_diff":-28.0,"publish_time_month_diff":-1.0}]'''
    # # #
    # # # # 选择模型并回滚
    # #
    client = ModelInferenceClient("http://en-search.seewo.com/ts-ex-cpu-1/inference/")
    print(client.inference("en_rec_lgbm", json_str))

