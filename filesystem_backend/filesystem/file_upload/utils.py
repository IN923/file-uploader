class GDrive_API:
    DRIVE_SCOPE = ["https://www.googleapis.com/auth/drive"]
    DOWNLOAD_FOLDER_ID="1dcF80lijoV2dWfJtDcMvHDvYNM9JTkdG"
    UPLOAD_FOLDER_ID="1Te73abx9QJQPNbUZj4ttX4Gdievx1QfV"

    def __init__(self):
        self.creds = None
        path = r'/mnt/c/Users/inder.DESKTOP-CFTSNU2/Desktop/company assignment/filesystem_backend/filesystem'
        filepath = os.path.join(path,'token.pickle')
        print(f'path={filepath}',os.path.exists(filepath))

        if os.path.exists(filepath):
            print("file exists")
            with open(filepath,'rb') as token:
                print("file exists11111")
                self.creds = pickle.load(token)
                print("creds scope=",self.creds.scopes,creds.valid)

        print("credentails")
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json',DRIVE_SCOPE)
                self.creds = flow.run_local_server(port=0)

        with open('token.pickle','wb') as token:
            pickle.dump(self.creds,token)

        return self.creds

    def build_drive_service(self):
        self.drive_service = None
        if creds:
            self.drive_service = build('drive','v3',credentials=self.creds)

        return self.drive_service

    def getFileList():
        if not service:
            return
        
        self.files = []
        query = f"'{DOWNLOAD_FOLDER_ID}' in parents and trashed=false"
        
        while True:
            results = self.drive_service.files().list(q=query,fields="nextPageToken,files(id,name,mimeType)",pageSize=100).execute()
            file_list = results.get('files',[])
            self.files.extend(file_list)

            if not results.get('nextPageToken',None):
                break

        return self.files

    
    



