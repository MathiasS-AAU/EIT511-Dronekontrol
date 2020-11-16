#ifndef UNICODE
#define UNICODE
#endif

#define WIN32_LEAN_AND_MEAN

#include"udp.h"
// Link with ws2_32.lib
#pragma comment(lib, "Ws2_32.lib")
WSADATA wsaData;

SOCKET SendSocket = INVALID_SOCKET;
sockaddr_in RecvAddr;

int InitUDP(const char* IP, unsigned short Port)
{

	int iResult;

	//unsigned short Port = 5004;
	char RecvBuf[1024];
	char SendBuf[1024];
	int BufLen = 1024;

	//----------------------
	// Initialize Winsock
	iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
	if (iResult != NO_ERROR) {
		wprintf(L"WSAStartup failed with error: %d\n", iResult);
		return -1;
	}

	//---------------------------------------------
	// Create a socket for sending data
	SendSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (SendSocket == INVALID_SOCKET) {
		wprintf(L"socket failed with error: %ld\n", WSAGetLastError());
		WSACleanup();
		return -1;
	}

#pragma warning(disable:4996) 
	//---------------------------------------------
	// Set up the RecvAddr structure with the IP address of
	// the receiver (in this example case "192.168.1.1")"192.168.137.146"
	// and the specified port number.
	RecvAddr.sin_family = AF_INET;
	RecvAddr.sin_port = htons(Port);
	RecvAddr.sin_addr.s_addr = inet_addr(IP);
}

int SendDataUDP(char* SendBuf, unsigned int BufLen)
{
	//---------------------------------------------
	// Send a datagram to the receiver
	int iResult;
	wprintf(L"Sending a datagram to the receiver...\n");
	iResult = sendto(SendSocket,
		SendBuf, BufLen, 0, (SOCKADDR*)&RecvAddr, sizeof(RecvAddr));
	if (iResult == SOCKET_ERROR) {
		wprintf(L"sendto failed with error: %d\n", WSAGetLastError());
		closesocket(SendSocket);
		WSACleanup();
		return -1;
	}
	return 0;
}

int closeUDP()
{
	int iResult;
	wprintf(L"Finished sending. Closing socket.\n");
	iResult = closesocket(SendSocket);
	if (iResult == SOCKET_ERROR) {
		wprintf(L"closesocket failed with error: %d\n", WSAGetLastError());
		WSACleanup();
		return -1;
	}
	//---------------------------------------------
	// Clean up and quit.
	wprintf(L"Exiting.\n");
	WSACleanup();
}