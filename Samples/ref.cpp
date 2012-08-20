#include <iostream>
#include <string>
#include <fstream>
#define MAX_MSG 500
using namespace std;

int main(){
	string input;
	//fstream f("log.txt", ios_base::in|ios_base::out|ios_base::trunc);
	while(1){
		input = "";
		getline(cin, input, '\n');
		if(input =="[quit]"){
			cout<<"[quitting]"<<endl;
			break;
		}else if (input == ""){
			continue;
		}
		//f<<input<<endl;
		//f<<"[The Narwhal, with the bacon, at midnight]"<<endl;
		cout<<"[The Narwhal, with the bacon, at midnight]"<<endl;
	}
	//f.close();
	return 0;
}