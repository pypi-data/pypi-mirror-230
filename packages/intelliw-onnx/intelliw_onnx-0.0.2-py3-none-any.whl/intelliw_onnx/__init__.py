from intelliw_onnx.convert import __version__ as convert_version
__version__ = "0.0.2"

logo = f"""\033[92m
--------------------------------------------------------------
         ⓐ                    _    _    ⓘ
         _  _ __    _    ___ | |  | |   _  _     _      
        | || '_ \ _| |_ / _ \| |  | |  | |\ _ _ / /     
        | || | | |_   _|  __/| |__| |__| | \  _  /    
        |_||_| |_| |___|\___| \____\___|_|  \/ \/    ONNX   
    
           intelliw-onnx  -- {__version__} Version --
           convert        -- {convert_version} Version --
--------------------------------------------------------------\033[0m
"""
print(logo, flush=True)
