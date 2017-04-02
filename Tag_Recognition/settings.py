

TRIANGLE_TYPE = 'triangle'
SQUARE_TYPE = 'square'
DOUBLE_SQUARE_TYPE = 'double_square'

AREA_RATIO_KEY = 'area_ratio'

tags_settings = {
                    'double_square' : {
                        'area_ratio' : 1.44
                    },
                    'square' : {
                        'area_ratio' : 2.205175
                    },
                    'triangle' : {
                        'area_ratio' : 1.812898
                    }
                }

camera_settings = {
    'resolution' : (640,480),
    'framerate' : 30,
    'frame': {
        'format' : "bgr",
        'use_video_port' : True
    }
}
