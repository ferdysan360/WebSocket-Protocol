# WebSocket-Protocol
## A Simple WebSocket Protocol - Dojima Family


### Petunjuk Penggunaan Program

#### Menjalankan Server dan Client
 1. Jalankan `server.py` dari terminal  
 2. Jalankan `client.html` dengan *browser* (dilakukan pihak penguji)  

#### Menjalankan Fungsionalitas Program `echo`  (dilakukan pihak penguji)
 1. Ketikkan *`!echo `* sebelum kalimat yang ingin dikirim kembali oleh server.  
> Contoh:  
> - *`!echo Dojima Family`*  

 2. Server akan memberi balasan berupa *Dojima Family* dan ditampilkan di browser.  

#### Menjalankan Fungsionalitas Program `submission` (dilakukan pihak penguji)
 1. Jalankan `server.py` dari terminal.  
 2. Jalankan `client.py` dari terminal.  
 3. Data hasil berupa *byte* dari *file* `client.zip` akan ditampilkan di dalam terminal.

#### Menjalankan Fungsionalitas Program untuk Mengirim *Binary File* (dilakukan pihak penguji)
 1. Masukkan data berupa *byte* pada *browser*.  
 2. Server akan melakukan pengecekan dengan *`md5` checksum*   
 3. Apabila *binary* cocok, akan diberi keluaran *1*, sebaliknya diberi keluaran *0*  


### *User Guide*

#### *Starting Server and Client*
*1. Run `server.py` using terminal*  
*2. Run `client.html` using any browser of your choice*  

#### *Using Program Utility* `echo`  
*1. Write down `!echo ` before your intended sentences.*  
> *Example:*  
> - *`!echo Dojima Family`*   

*2. Server will send a reply with **Dojima Faimly** in browser.*  

#### *Using program utility* `submission`  
*1. Run `server.py` from terminal*  
*2. Run `client.py` from terminal*  
*3. Data result in form of byte from `client.zip` will be printed in terminal window*

#### *Using Program Utility to Send Binary File*
*1. Insert your byte data to browser*  
*2. Server will check it using `md5` checksum*   
*3. If the two give the same binary result, server will send an output of '1' to the browser, else the output will be '0'* 


### Pembagian Tugas
| NIM      | Nama               | Apa yang dikerjakan        | Persentasi kontribusi |
|:--------:|:------------------:|:--------------------------:|:---------------------:|
| 13517116 | Ferdy Santoso      | Echo, Analysis, Debug      |                    30%|
| 13517125 | Christzen Leonardy | Submission, File, Analysis |                    45%|
| 13517146 | Hansen             | Echo, Analysis, Doc        |                    25%|
