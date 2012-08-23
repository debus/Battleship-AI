#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#define MAX_MESSAGE_LENGTH 512

int get_line(char* buffer, size_t size, size_t* num_read = NULL,int keep_newline=FALSE);

int main(int argc, char** argv){
	char message[MAX_MESSAGE_LENGTH + 1];
	//get_line(message, MAX_MESSAGE_LENGTH + 1);
	printf("%s",message);
	return 0;
}

size_t get_line(char* buffer, size_t size, size_t* num_read,int keep_newline){
	if(buffer == NULL || size == 0)
		return 0;
	char* pC = buffer;
	--size;
	for(size_t i = 0; i < size; ++i){
		char c = getchar();
		if(c == '\n'){
			if(keep_newline != FALSE){
				*pC = '\n';
				pC[1] = '\0';
				if(num_read)
					*num_read = i+1;
				return 0;
			}else{
				if(num_read)
					*num_read = i;
				return 0;
			}
		}
		*pC = c;
		++pC;
	}
	if(keep_newline == FALSE){
		char c = getchar();
		if(c == '\n'){
			*pC = '\0';
			
		}
	}
}