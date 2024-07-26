import globalFunctions

while True:
    
    print(f"""Welcome to the BadRat, DriveEncryption! Version {globalFunctions.GetProgramVersion()}""")
    
    print("""\n[WARNING]: By using this software to encrypt or decrypt your files, you accept full responsibility for any issues that may arise. We are not liable for any damages during this process. Using this software for malicious or illegal purposes is strictly prohibited and can result in severe legal consequences. Please use this software ethically and in compliance with all applicable laws and regulations.""")

    selected_drive = str(input("\nPlease input a drive you want to encrypt: (e.g. 'C', 'D', 'E'): "))
    continue_encryption = str(input("\n\n[WARNING]: ARE YOU SURE YOU WANT TO CONTINUE? *THERE IS ABSOLUTELY NO GOING BACK, DOING THIS WILL ENCRYPT FILES, DELETE IMAGES, AND VIDEOS! THIS IS UNRECOVERABLE* Y/N: "))
    
    if continue_encryption in ('Y', 'y'):
        
        globalFunctions.EncryptFiles(globalFunctions.GetDesignatedDrive(selected_drive))
    
    else:
        
        quit()
    
    quit()