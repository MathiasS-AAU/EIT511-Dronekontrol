#pragma once
#include <winsock2.h>
#include <Ws2tcpip.h>
#include <stdio.h>
#include <string>

int InitUDP(const char* IP, unsigned short Port); // example: InitUDP("192.168.137.146", 5004);

int SendDataUDP(char* SendBuf, unsigned int BufLen);

int closeUDP();