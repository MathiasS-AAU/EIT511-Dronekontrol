#include "DataStreamClient.h"

#include <boost/lexical_cast.hpp>

#include <cassert>
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>

#include"udp.h"

#if defined _WIN64 || defined WIN32
#include <conio.h>   // For _kbhit()
#include <cstdio>   // For getchar()
#include <windows.h> // For Sleep()
#else
#include <unistd.h> // For sleep()
#endif // WIN32 or _WIN64

#define CSV_OUTPUT( FILE, OUTPUT ) if( FILE.good() ) FILE << OUTPUT

//Læs resultatets enum værdi og giv string
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
#define OBJECT "LOL"
#define SEGMENT "LOL"

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

#define PI 3.14159265359
// Main loop
int main() {
    // Setup UDP connection with IPv4 and port
    InitUDP("192.168.137.146", 5004);

    ViconDataStreamSDK::CPP::Client MyClient;// Creating the client for ViconSDK
    //Connecting to Vicon Server
    ViconDataStreamSDK::CPP::Output_Connect connection = MyClient.Connect("localhost");
    std::cout << "Conneting: " << resultEnumParse(connection.Result) << "\n";

    //Enabling tracking data
    std::cout << "Enable Segment Data: " << resultEnumParse(MyClient.EnableSegmentData().Result) << "\n";

    //Unions for conversion to bytes
    doubleArray2char Rot;
    doubleArray2char Pos;
    uint64_t2char i;
    i.i = 0;

    while (1) // Press Esc to end loop
    {
        // Get one frame of data
        std::cout << "Get Frame: " << resultEnumParse(MyClient.GetFrame().Result) << "\n";
        //check if Object and Segment are correct
        std::cout << "Get Rotation: " << resultEnumParse(MyClient.GetSegmentGlobalRotationEulerXYZ(OBJECT, SEGMENT).Result) << "\n";
        //Read rotation and translation
        double* rotation = MyClient.GetSegmentGlobalRotationEulerXYZ(OBJECT, SEGMENT).Rotation;
        double* translation = MyClient.GetSegmentGlobalTranslation(OBJECT, SEGMENT).Translation;
        //print the raw position and rotation
        std::cout << "Rotation X:" << rotation[0] << " Y: " << rotation[1] << " Z: " << rotation[2] << "\n";
        std::cout << "Position X:" << translation[0] << " Y: " << translation[1] << " Z: " << translation[2] << "\n";
        //Stop and wait for keyboard press
        char c = _getch();

        // convert data to correct units and ready for insertion to packet
        Rot.d[0] = rotation[0] * 180.0 / PI; Rot.d[1] = rotation[1] * 180.0 / PI; Rot.d[2] = rotation[2] * 180.0 / PI;
        Pos.d[0] = translation[0] * 1000.0; Pos.d[1] = translation[1] * 1000.0; Pos.d[2] = translation[2] * 1000.0;

        //Create packet
        char Packet[56];
        //Print contents of packet
        std::cout << "Sending packet: " << "Pos = " << Pos.d[0] << " " << Pos.d[1] << " " << Pos.d[2] 
            << " Rot = " << Rot.d[0] << " " << Rot.d[1] << " " << Rot.d[2] 
            << " Packet number: " << i.i << "\n";

        //Inserting data into packet
        for (int j = 0; j < 24; j++)
        {
            Packet[j] = Pos.c[j];
        }
        for (int j = 0; j < 24; j++)
        {
            Packet[j + 24] = Rot.c[j];
        }
        for (int j = 0; j < 8; j++)
        {
            Packet[j + 48] = i.c[j];
        }

        //Print packet in hexadecimal
        std::cout << "Packet binary content:";
        for (int i = 0; i < 56; i++)
        {
            printf("%2X", Packet[i]);
        }
        std::cout << "\n";

        //Send packet
        SendDataUDP(Packet,56);
        if (c == 27) break;
        i.i++;
    }
    //Disconnect from SDK
    std::cout << "Disconnecting: " << resultEnumParse(MyClient.Disconnect().Result) << "\n";
    system("pause");
    return 1;
}