#!/usr/bin/env -S tcc -run
#include <stdio.h>

int main(int argc, char** argv){
    if (argc > 1){
        FILE* f = fopen(argv[1], "r");
        short offset = 0;
        char str[128];
        if(f){
            fseek(f, 0x20E, SEEK_SET);
            fread(&offset, 2, 1, f);
            fseek(f, offset + 0x200, SEEK_SET);
            fread(str, 128, 1, f);
            str[127] = '\0';
            printf("%s\n", str);
            fclose(f);
            return 0;
        }else {
            return 2;
        }
    } else {
        printf("use: kver [kernel image file]\n");
        return 1;
    }
}
