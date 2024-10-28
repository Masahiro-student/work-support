/*
    MIR2-13W_体性感覚伝達モジュール制御用ソフトウェア
    MIR2-13W.ino
    UTF-8

    更新履歴
    2023.12.18　新規作成

    免責事項
        当社は、本プログラムを配布するにあたって、その内容、機能等について細心の注意を払っておりますが、
        お客様の利用環境での動作を保証をするものではなく、
        本プログラムのご利用により、万一、ご利用者様に何らかの不都合や損害が発生したとしても何らの責任を負うものではありません。
        また、当社は通知することなく本プログラムの情報の訂正、修正、追加、更新停止、削除等をいつでも行うことができるものとします。
*/

/**
 * @file MIR2-13W.ino
 * @author Saitoh Syuuhei (saitoh-sh@koganei.co.jp)
 * @brief MIR2-13W_体性感覚伝達モジュール制御用ソフトウェア
 * @version 0.1
 * @date 2023-12-13
 * 
 * 
 */
#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include <FlexiTimer2.h>
#include "Debug.h" 

#define ARRAY_SIZE(x) (sizeof(x)/sizeof(x[0]))

/**
 * @name Error message
 * @{
 */
#define Error1 "Out of input range"  //!< 入力された設定値が範囲外のとき
#define Error2 "Check your input" //!< 入力されたコマンドが一致しなかったとき
/** @} */

/**
 * @name Motor
 * @{
 */
#define Motor_A 29 //!< motor_num 0 MIL_A 4
#define Motor_B 28 //!< motor_num 1 MIL_A 5
#define Motor_C 27 //!< motor_num 2 MIL_A 6
#define Motor_D 26 //!< motor_num 3 MIL_A 7
#define Motor_E 25 //!< motor_num 4 MIL_A 8
#define Motor_F 24 //!< motor_num 5 MIL_A 9
#define Motor_G 23 //!< motor_num 6 MIL_A 10
#define Motor_H 22 //!< motor_num 7 MIL_A 11
#define Motor_I 14 //!< motor_num 8 MIL_A 12
#define Motor_J 15 //!< motor_num 9 MIL_A 13
#define Motor_K 69 //!< motor_num 10 MIL_A 3
#define Motor_L 68 //!< motor_num 11 MIL_A 2
#define Motor_M 65 //!< motor_num 12 MIL_B 2 
#define Motor_N 64 //!< motor_num 13 MIL_B 3 
#define Motor_O 44 //!< motor_num 14 MIL_B 7
#define Motor_P 18 //!< motor_num 15 MIL_B 10
/** @} */

/**
 * @name Valve
 * @{
 */
#define Valve1 4 //!< valve_num_0
#define Valve2 5 //!< valve_num_1
#define Valve3 6 //!< valve_num_2
#define Valve4 7 //!< valve_num_3
#define Valve5 8 //!< valve_num_4
#define valve_num_0 0
#define valve_num_1 1
#define valve_num_2 2
#define valve_num_3 3
#define valve_num_4 4
/**@}*/


/**
 * @brief コンプレッサコミュニケーション用
 * 
 * @name Compressor
 * @{
 */
#define RE 40
#define DE 41

String Comp_Receive_Str; //!< コンプレッサより受け取った文字列
char Comp_Receive_Buff[30]; //!< 受信バッファ
unsigned int befor_bit_0 = 0; //!< スイッチ入力の変更前
unsigned int befor_bit_1 = 0; //!< スイッチ入力の変更前

int press_set_flag = 0; //!< 圧力設定フラグ Low：通信 High：トグルスイッチ
int Max_Presser = 401; //!< 圧力設定最大値
int Min_Presser = 99; //!< 圧力設定最小値
/**@}*/

/**
 * 
 * @name Motor
 * @{
 */
//! motor_state[][] = {output_port,onoff_state,duty}
//! デューティ初期値：0%(停止)
long motor_state[ ][3] = {
    {Motor_A,0,0},
    {Motor_B,0,0},
    {Motor_C,0,0},
    {Motor_D,0,0},
    {Motor_E,0,0},
    {Motor_F,0,0},
    {Motor_G,0,0},
    {Motor_H,0,0},
    {Motor_I,0,0},
    {Motor_J,0,0},
    {Motor_K,0,0},
    {Motor_L,0,0},
    {Motor_M,0,0},
    {Motor_N,0,0},
    {Motor_O,0,0},
    {Motor_P,0,0},
};


int time_count[ ] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}; //!< モータ毎の時間管理
int motor_period = 100; //!< PWM周期
int Max_Duty = 101; //!< Duty比設定最大値
unsigned int motor_num =0; //!< モータカウンター

unsigned int Number_of_motor = 16;    //!< 接続されているモータ数
/**@}*/

/**
 * @brief シリアルコマンド
 * @name Command
 * @{
 */
//! コマンドの種類を表すCommand列挙型の定義
enum Command{
    Command_motor = 0,
    Command_allmotor,
    Command_prm,
    Command_valve,
    Command_mod,
    Command_stop,
    Command_comp,
    Command_Num
};

#define Command_MaxNumber (Command_Num + 1)

String g_cmds[3]; //!< シリアル文字列処理
String g_data[3]; //!< シリアル文字列処理
char send_text[255]; //!< 出力用文字列格納配列
unsigned int select_config = 0;
unsigned int number_count = 0;
unsigned int config_number = 0;
/**@}*/

/**
 * @name Valve
 * @{
 */
long valve_state[ ] ={0,0,0,0,0}; //!< バルブ状態保存
int Number_of_valves = 5; //!< 搭載バルブ数
/**@}*/

/**
 * @name interrupts
 * @{
 */
/**
 * @brief PWM生成用のタイマ割り込み
 * 
 */
void timer()
{
    for(unsigned int i = 0; i < Number_of_motor; i++)
    {
        time_count[i]++;
    }
    OutputPort(motor_num);
    motor_num++;
    if(motor_num == Number_of_motor)
    {
        motor_num = 0;
    }
}

/**
 * @brief ポート制御
 * 
 * @param number ON/OFFするモータ番号
 */
void OutputPort(int number)
{
    if(motor_state[number][2] == 0)
    {
        digitalWrite(motor_state[number][0],LOW);
        time_count[number] = 0;
        motor_state[number][1] = 0;
    }else{
        if(motor_state[number][1] == 1)
        {
            if(time_count[number] >= motor_state[number][2])
            {
                digitalWrite(motor_state[number][0],LOW);
                time_count[number] = 0;
                motor_state[number][1] = 0;
            }
        }else{
            if(time_count[number] >= (motor_period - motor_state[number][2]))
            {
                digitalWrite(motor_state[number][0],HIGH);
                time_count[number] = 0;
                motor_state[number][1] = 1;
            }
        }
    }
}
/**@}*/

/**
 * @name Compressor
 * @{
 */
/**
 * @brief コンプレッサ通信
 * 
 * @param data 
 */
void Send_Data(String data)
{
    digitalWrite(RE, HIGH); // レシーバDisenable
    digitalWrite(DE, HIGH); // ドライバEnable
    Serial2.println(data);
    Serial2.flush();    //送信待ち
    digitalWrite(RE, LOW);  // レシーバEnable
    digitalWrite(DE, LOW); // ドライバDisenable
}

/**
 * @brief 485 buffer clear
 * 
 */
void Receive_Buff_Clear()
{
    for(int i = 0; i < 30; i++)
    {
        Comp_Receive_Buff[i] = '\0';
    }
}

/**
 * @brief コンプレッサ停止圧力設定
 * トグルスイッチ0と1を使用して設定する。
 * 00 : 100[kPa]
 * 01 : 200[kPa]
 * 10 : 300[kPa]
 * 11 : 400[kpa]
 */
void Presser_Set()
{
    unsigned int press_Bit_0 = digitalRead(A5);
    unsigned int press_Bit_1 = digitalRead(A4);

    DebugVariable("press_Bit_0",press_Bit_0);
    DebugVariable("press_Bit_1",press_Bit_1);

    if((press_Bit_1 != befor_bit_1) || (press_Bit_0 != befor_bit_0))
    {
        befor_bit_1 = press_Bit_1;
        befor_bit_0 = press_Bit_0;
        if(press_Bit_1 == 0 && press_Bit_0 == 0)
        {
            Send_Data("@0,W-P_STOP,100");
            Serial.println("Set 100[kPa]");
        }

        if(press_Bit_1 == 0 && press_Bit_0 == 1)
        {
            Send_Data("@0,W-P_STOP,200");
            Serial.println("Set 200[kPa]");
        }

        if(press_Bit_1 == 1 && press_Bit_0 == 0)
        {
            Send_Data("@0,W-P_STOP,300");
            Serial.println("Set 300[kPa]");
        }

        if(press_Bit_1 == 1 && press_Bit_0 == 1)
        {
            Send_Data("@0,W-P_STOP,400");
            Serial.println("Set 400[kPa]");
        }
    }
}
/**@}*/

/**
 * @name Valve
 * @{
 */
/**
 * @brief 指定したバルブの状態を変更する
 * 
 * @param valve 
 * @param state 
 */
void Valve_Fire(int valve, int state)
{
    switch (valve)
    {
    case valve_num_0:
        digitalWrite(Valve1,state);
        valve_state[valve] = state;
        break;
    case valve_num_1:
        digitalWrite(Valve2,state);
        valve_state[valve] = state;
        break;
    case valve_num_2:
        digitalWrite(Valve3,state);
        valve_state[valve] = state;
        break;
    case valve_num_3:
        digitalWrite(Valve4,state);
        valve_state[valve] = state;
        break;
    case valve_num_4:
        digitalWrite(Valve5,state);
        valve_state[valve] = state;
        break;
    
    default:
        break;
    }
}
/**@}*/

/**
 * @name Command
 * @{
 */
/**
 * @brief 文字列を区切り文字にて分割する
 * 
 * @param data 文字列
 * @param delimiter 区切り文字
 * @param dst 格納先
 * @return int 
 */
int split(String data , char delimiter , String *dst)
{
    int index = 0;
    int ArraySize = (sizeof(data) / sizeof((data)[0]));
    int datalength = data.length();
    for(int i = 0; i < datalength; i++)
    {
        char tmp = data.charAt(i);
        if(tmp == delimiter)
        {
            index++;
            if(index > (ArraySize - 1)) return -1;
        }
        else dst[index] += tmp;
    }
    return (index + 1);
}

/**
 * @brief 受信したコマンドに応じた処理
 * 
 * @param serial_data 
 */
void SerialCheck(String serial_data)
{
    char const* const set_config[ ] = { "MOTOR",
                                        "ALLMOTOR",
                                        "PRM",
                                        "VALVE",
                                        "MOD",
                                        "STOP",
                                        "COMP"};

    // 区切り文字「:」で入力された文字列を分割する
    int index = split(serial_data, ':', g_cmds);
    
    for(int i = 0; i < index; i++)
    {
        g_data[i] = g_cmds[i];
    }

    // 配列のクリア
    for(unsigned int i = 0; i < ARRAY_SIZE(g_cmds); i++)
    {
        g_cmds[i] = '\0';
    }

    // 入力と一致するコマンドを探す
    for(int i = 0; i < Command_MaxNumber; i++)
    {
        select_config = g_data[0].equalsIgnoreCase(String(set_config[i]));
        if(select_config == 1)
        {
            config_number = number_count;
            break;
        }
        number_count++;
    }

    // 一致しなかったとき
    if(number_count == Command_MaxNumber)
    {
        config_number = 99;
    }
    DebugVariable("config_number",config_number);
    
    // コマンド毎の処理
    switch (config_number)
    {
    case Command_motor:
        {
            long set_motor_num = g_data[1].toInt();
            long receive_duty = g_data[2].toInt();

            if((receive_duty < Max_Duty) && (set_motor_num < Number_of_motor))
            {
                motor_state[set_motor_num][2] = receive_duty;
                sprintf(send_text,
                        "Motor No: %ld\nSet Duty: %ld%%",
                        set_motor_num,
                        motor_state[set_motor_num][2]);
                Serial.println(send_text);
            }else{
                Serial.println(Error1);
            }
        }
        break;

    case Command_allmotor:
        {
            long receive_duty = g_data[1].toInt();
            
            if(receive_duty < Max_Duty)
            {
                for(unsigned int i = 0; i < Number_of_motor; i++)
                {
                    motor_state[i][2] = receive_duty;
                }
                
                sprintf(send_text,"Set Duty: %ld%%",receive_duty);
                Serial.println(send_text);
            }else{
                Serial.println(Error1);
            }
        }
        break;

    case Command_prm:
        {
            long set_motor_num = g_data[1].toInt();

            if(set_motor_num < Number_of_motor)
            {
                sprintf(send_text,
                        "Motor No: %ld Duty: %ld%%",
                        set_motor_num,
                        motor_state[set_motor_num][2]);
                Serial.println(send_text);
            }else{
                Serial.println(Error1);
            }
        }
        break;

    case Command_valve:
        {
            long set_valve_num = g_data[1].toInt();
            long set_valve_state = g_data[2].toInt();

            if(set_valve_num < Number_of_valves)
            {
                Valve_Fire(set_valve_num,set_valve_state);

                if(set_valve_state)
                {
                    sprintf(send_text,"Valve No: %ld ON",set_valve_num);
                    Serial.println(send_text);
                }else{
                    sprintf(send_text,"Valve No: %ld OFF",set_valve_num);
                    Serial.println(send_text);
                }
            }else{
                Serial.println(Error1);
            }
        }
        break;

    case Command_mod:
        {
            long receive_state = g_data[1].toInt();

            if(receive_state < 3)
            {
                press_set_flag = receive_state;
                if(press_set_flag)
                {
                    Serial.println("SW Enable");
                }else{
                    Serial.println("SW Disenable");
                }
            }else{
                Serial.println(Error1);
            }
        }
        break;

    case Command_stop:
        {
            long receive_stop_press = g_data[1].toInt();
            
            if((receive_stop_press < Max_Presser) && (Min_Presser < receive_stop_press))
            {
                sprintf(send_text,"@0,W-P_STOP,%ld",receive_stop_press);
                Send_Data(send_text);
                sprintf(send_text,"Set %ld[kPa]",receive_stop_press);
                Serial.println(send_text);
            }else{
                Serial.println(Error1);
            }
        }
        break;

    default:
        Serial.println(Error2);
        break;
    }

    // 各種変数の初期化
    for(int i = 0; i < 3; i++)
    {
        g_data[i] = '\0';
    }
    config_number = 0;
    select_config = 0;
    number_count = 0;
}
/**@}*/


/**
 * @brief ピン設定など
 * 
 */
void setup()
{
    Serial.begin(9600); // シリアルモニタ用
    Serial2.begin(9600,SERIAL_8O1); // コンプレッサ用シリアル設定 9600bps 8bit Odd stop 1bit

    pinMode(Motor_A,OUTPUT);
    pinMode(Motor_B,OUTPUT);
    pinMode(Motor_C,OUTPUT);
    pinMode(Motor_D,OUTPUT);
    pinMode(Motor_E,OUTPUT);
    pinMode(Motor_F,OUTPUT);
    pinMode(Motor_G,OUTPUT);
    pinMode(Motor_H,OUTPUT);
    pinMode(Motor_I,OUTPUT);
    pinMode(Motor_J,OUTPUT);
    pinMode(Motor_K,OUTPUT);
    pinMode(Motor_L,OUTPUT);
    pinMode(Motor_M,OUTPUT);
    pinMode(Motor_N,OUTPUT);
    pinMode(Motor_O,OUTPUT);
    pinMode(Motor_P,OUTPUT);

    // バルブポート
    pinMode(Valve1,OUTPUT);
    pinMode(Valve2,OUTPUT);
    pinMode(Valve3,OUTPUT);
    pinMode(Valve4,OUTPUT);
    pinMode(Valve5,OUTPUT);

    // 485通信にて使用
    pinMode(RE,OUTPUT);
    pinMode(DE,OUTPUT);

    // 圧力設定用
    pinMode(A5,INPUT);
    pinMode(A4,INPUT);

    digitalWrite(RE, HIGH); // レシーバDisenable
    digitalWrite(DE, HIGH); // ドライバEnable

    FlexiTimer2::set(1,1.0/10000,timer);
    FlexiTimer2::start(); // 割込み開始
    DebugPrint("ON MIR2-13W");
}

/**
 * @brief メインループ
 *  シリアルモニタからの入力を待ち、コマンドに応じた処理を行う
 *  Press_Set()はコンプレッサへの圧力変更を行う関数だが、今回は初期値でSW無効としているため通らない
 */
void loop()
{

    if(press_set_flag)
    {
        DebugPrint("in press");
        Presser_Set();
    }

    if(Serial.available())
    {
        DebugPrint("get serial");
        SerialCheck(Serial.readStringUntil('\n'));
    }

    if(Serial2.available())
    {
        Comp_Receive_Str = Serial2.readStringUntil('\r');
        Comp_Receive_Str.toCharArray(Comp_Receive_Buff,30);
        DebugPrint(Comp_Receive_Buff);
        Receive_Buff_Clear();
    }
}