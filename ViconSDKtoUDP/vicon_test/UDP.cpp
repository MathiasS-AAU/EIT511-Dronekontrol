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



	/*struct addrinfo* result = NULL, * ptr = NULL, hints;

	ZeroMemory(&hints, sizeof(hints));
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_DGRAM;
	hints.ai_protocol = IPPROTO_UDP;
	hints.ai_flags = AI_PASSIVE;

	iResult = getaddrinfo(NULL, "5005", &hints, &result);
	if (iResult != 0) {
		printf("getaddrinfo failed: %d\n", iResult);
		WSACleanup();
		return 1;
	}*/
	//---------------------------------------------
	// Create a socket for sending data
	SendSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (SendSocket == INVALID_SOCKET) {
		wprintf(L"socket failed with error: %ld\n", WSAGetLastError());
		WSACleanup();
		return -1;
	}

	/*iResult = bind(SendSocket, result->ai_addr, (int)result->ai_addrlen);
	if (iResult == SOCKET_ERROR) {
		printf("bind failed with error: %d\n", WSAGetLastError());
		freeaddrinfo(result);
		closesocket(SendSocket);
		WSACleanup();
		return 1;
	}*/

#pragma warning(disable:4996) 
	//---------------------------------------------
	// Set up the RecvAddr structure with the IP address of
	// the receiver (in this example case "192.168.1.1")"192.168.137.146"
	// and the specified port number.
	RecvAddr.sin_family = AF_INET;
	RecvAddr.sin_port = htons(Port);
	RecvAddr.sin_addr.s_addr = inet_addr(IP);

	/*    wprintf(L"Recieving a datagram from the receiver...\n");
	iResult = recvfrom(SendSocket,RecvBuf, BufLen, 0, NULL, NULL);
	if (iResult == SOCKET_ERROR) {
		wprintf(L"recvfrom failed with error: %d\n", WSAGetLastError());
		closesocket(SendSocket);
		WSACleanup();
		return 1;
	}
	char lol[512];
	strncpy_s(lol, RecvBuf, 100);
	sprintf_s(SendBuf, "Lmao: %s", lol);
	printf("%s\n",SendBuf);*/
	//---------------------------------------------
	// Send a datagram to the receiver
	wprintf(L"Sending a datagram to the receiver...\n");
	{
		iResult = sendto(SendSocket,
			SendBuf, BufLen, 0, (SOCKADDR*)&RecvAddr, sizeof(RecvAddr));
		if (iResult == SOCKET_ERROR) {
			wprintf(L"sendto failed with error: %d\n", WSAGetLastError());
			closesocket(SendSocket);
			WSACleanup();
			return -1;
		}
	}    //---------------------------------------------
	// When the application is finished sending, close the socket.
	return 0;
}

int SendDataUDP(char* SendBuf, unsigned int BufLen)
{
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