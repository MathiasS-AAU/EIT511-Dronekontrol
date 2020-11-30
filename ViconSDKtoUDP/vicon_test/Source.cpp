#include "DataStreamClient.h"

#include <boost/lexical_cast.hpp>

#include <iostream>

#include <chrono>

#include"udp.h"

#if defined _WIN64 || defined WIN32
#include <conio.h>   // For _kbhit()
#include <cstdio>   // For getchar()
#include <windows.h> // For Sleep()
#else
#include <unistd.h> // For sleep()
#endif // WIN32 or _WIN64

#define CSV_OUTPUT( FILE, OUTPUT ) if( FILE.good() ) FILE << OUTPUT

//Read the result enum value and return a string
std::string resultEnumParse(unsigned int Result) 
{
    switch(Result)
    {
    case 1:
        return "Not Implemented";
    case 2:
        return "Success";
    case 3:
        return "Invalid Host Name";
    case 4:
        return "Invalid Multicast IP";
    case 5:
        return "Client Already Connected";
    case 6:
        return "Client Connection Failed";
    case 7:
        return "Server Already Transmitting Multicast";
    case 8:
        return "Server Not Transmitting Multicast";
    case 9:
        return "Not Connected";
    case 10:
        return "No Frame";
    case 11:
        return "Invalid Index";
    case 12:
        return "Invalid Camera Name";
    case 13:
        return "Invalid Subject Name";
    case 14:
        return "Invalid Segment Name";
    case 15:
        return "Invalid Marker Name";
    case 16:
        return "Invalid Device Name";
    case 17:
        return "Invalid Device Output Name";
    case 18:
        return "Invalid Latency Sample Name";
    case 19:
        return "CoLinear Axes";
    case 20:
        return "LeftHanded Axes";
    case 21:
        return "Haptic Already Set";
    }
    return "Unknown";
}

//Vicon object data to be tracked. Seems it needs to be identical.
//#define OBJECT "LOL"
//#define SEGMENT "LOL"
#define SEGMENT OBJECT

//Unions for conversion to bytes
union uint64_t2char
{
    uint64_t i;
    char c[8];
};
union double2char
{
    double d;
    char c[8];
};
union doubleArray2char
{
    double d[3];
    char c[24];
};


uint64_t GetMilli()
{
    using namespace std::chrono;
    milliseconds ms = duration_cast<milliseconds>(
        system_clock::now().time_since_epoch());
        return ms.count();
}
#define PI 3.14159265359
// Main loop
int main() {
    std::string IP;
    std::cout << "Input IP address of control system:\n";
    std::cin >> IP;

    std::string OBJECT;
    std::cout << "Input tracked object name:\n";
    std::cin >> OBJECT;
   

    // Setup UDP connection with IPv4 and port
    InitUDP(IP.c_str(), 5004);

    ViconDataStreamSDK::CPP::Client MyClient;// Creating the client for ViconSDK
    //Connecting to Vicon Server
    ViconDataStreamSDK::CPP::Output_Connect connection = MyClient.Connect("localhost");
    std::cout << "Conneting: " << resultEnumParse(connection.Result) << "\n";

    //Enabling tracking data
    std::cout << "Enable Segment Data: " << resultEnumParse(MyClient.EnableSegmentData().Result) << "\n";

    std::cout << "Get Frame: " << resultEnumParse(MyClient.GetFrame().Result) << "\n";
    //check if Object and Segment are correct
    std::cout << "Get Rotation: " << resultEnumParse(MyClient.GetSegmentGlobalRotationEulerXYZ(OBJECT, SEGMENT).Result) << "\n";

    //Unions for conversion to bytes
    doubleArray2char Rot;
    doubleArray2char Pos;
    uint64_t2char time;
    time.i = 0;

    while (1) // Press Esc to end loop
    {
        //How long ago was the last transmission?
        uint64_t timedif = GetMilli() - time.i;
        
        //wait at least x ms before sending.
        if (timedif >= 10) {
            std::cout << "timedif: " << timedif << "\n";
            // Get one frame of data
            MyClient.GetFrame();
            //check if Object and Segment are correct
            std::cout << "Get sample: " << resultEnumParse(MyClient.GetSegmentGlobalRotationEulerXYZ(OBJECT, SEGMENT).Result) << "\n";
            //Read rotation and translation
            double* rotation = MyClient.GetSegmentGlobalRotationEulerXYZ(OBJECT, SEGMENT).Rotation;
            double* translation = MyClient.GetSegmentGlobalTranslation(OBJECT, SEGMENT).Translation;

            // convert data to correct units and ready for insertion to packet
            Rot.d[0] = rotation[0] * 180.0 / PI; Rot.d[1] = rotation[1] * 180.0 / PI; Rot.d[2] = rotation[2] * 180.0 / PI;
            Pos.d[0] = translation[0] / 1000.0; Pos.d[1] = translation[1] / 1000.0; Pos.d[2] = translation[2] / 1000.0;

            //Create packet
            char Packet[56];
            //Print contents of packet
            std::cout << "Sending packet: " << "\nPos = " << Pos.d[0] << " " << Pos.d[1] << " " << Pos.d[2]
                << "\nRot = " << Rot.d[0] << " " << Rot.d[1] << " " << Rot.d[2]
                << "\nms since epoch: " << time.i << "\n";

            //Inserting data into packet
            for (int j = 0; j < 24; j++)
            {
                Packet[j] = Pos.c[j];
            }
            for (int j = 0; j < 24; j++)
            {
                Packet[j + 24] = Rot.c[j];
            }
            time.i = GetMilli();
            for (int j = 0; j < 8; j++)
            {
                Packet[j + 48] = time.c[j];
            }


            //Send packet
            SendDataUDP(Packet, 56);
        }
    }
    //Disconnect from SDK
    std::cout << "Disconnecting: " << resultEnumParse(MyClient.Disconnect().Result) << "\n";
    system("pause");
    return 1;
}