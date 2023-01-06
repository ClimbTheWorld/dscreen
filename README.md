# dscreen  
This project is a data viewer which collects data from different source using REST api and shows it on a e-paper display.  
## sample content
test  

# content
## dataflow
![Dataflow](20230106_Dataflow.drawio.png "Dataflow")  

## hardware  
Raspberry Pi Zero WH  
waveshare epd_5in83b_v2  
## software
Raspbian Bullseye (11)  
Python 3.9.2  
waveshare sample project https://github.com/waveshare/e-Paper 
### installation of the project
1 flash uSD card (4GB+) with latest Raspbian OS  
2 activate ssh (Raspberry Pi Imager has an option or create an empty file in /boot called "ssh")  
3 connect the parts together (see waveshare manual)  
4 startup the Raspberry Pi
5 login into Raspberry Pi using ssh
6 install using this command: $ wget https://github.com/climbtheworld/bootstrap_dscreen.sh && chmod +x bootstrap_dscreen.sh && sudo ./bootstrap_dscreen.sh  
### Links
#### e-Paper
https://www.waveshare.com/w/upload/8/89/5.83inch-e-paper-hat-user-manual-en.pdf  
https://www.waveshare.com/w/upload/8/89/5.83inch-e-paper-hat-user-manual-en.pdf  
https://www.waveshare.com/wiki/5.83inch_e-Paper_HAT_(B)  

