#ifndef __DEBUG_H__
#define __DEBUG_H__

#define DEBUG
#ifdef DEBUG
    // #define BeginDebugPrint()    Serial.begin( 9600 ) 本体でシリアル宣言してるため
    #define DebugPrint( message )\
        {\
            char __buff__[ 512 ];\
            sprintf( __buff__\
                    , "%s (Func:%s, Line:%d)"\
                    , message\
                    , __func__\
                    , __LINE__ );\
            Serial.println( __buff__ );\
            Serial.flush();\
        }
    #define DebugVariable(variable_name,variable)\
        {\
            char __buff__[512];\
            sprintf( __buff__\
                    , "%s,%d (Func:%s, Line:%d)"\
                    ,variable_name\
                    ,variable\
                    ,__func__\
                    ,__LINE__ );\
            Serial.println(__buff__);\
            Serial.flush();\
        }
#else
    // #define BeginDebugPrint()
    #define DebugPrint( message )
    #define DebugVariable(variable)
#endif // DEBUG
#endif // __DEBUG_H__