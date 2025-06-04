import asyncio 
import telnetlib3 
import nest_asyncio 
import datetime 
  
now = datetime.datetime.now() 
filename = now.strftime("%Y%m%d_%H%M_lte_radio.txt")

async def shell(reader, writer): 
    while True: 
        outp = await reader.read(1024) 
        if not outp: 
            break 

        # display all server output 
        print(outp, flush=True) 

        # write server output to txt 
        with open(filename, 'a') as file: 
            file.write(outp) 

        # commands to run and get output of the radio connection from the modem 

        if 'UserDevice login:' in outp: 
            writer.write('admin') # user name
            writer.write('\r\n') 

        elif 'Password:' in outp: 
            writer.write('Abcd@12345') # the password
            writer.write('\r\n') 

        elif 'UserDevice' in outp: 
            writer.write('AT+MGPSNMEA') # extract the GPS locaion and date_time information
            writer.write('\r\n') 
            writer.write('AT+MMSVRCELL') # extract the serving cell parameters
            writer.write('\r\n') 
            writer.write('AT+MMNEBCELL') # extract the Neighbor cells parameters
            writer.write('\r\n')
            


    # EOF 
    print() 

async def main(): 
    # Test after X seconds to be sure that the pMLTE is started and the connection is ready
    await asyncio.sleep(300) # change the value between parentheses to change the time (in seconds) to start exectuting this script
    reader, writer = await telnetlib3.open_connection('192.168.168.2', 23, shell=shell) # change the IP and port to match the device connected
    await writer.protocol.waiter_closed 

if __name__ == '__main__': 
    nest_asyncio.apply() 
    asyncio.run(main()) 

 
