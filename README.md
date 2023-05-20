# Sort-context-menu
This is a python script to add to the context menu some quality of life script to organize directory files.

### Features:
- Delete empty directories
- Extract all files inside a directory
- Sort all files inside a directory by their date
- - Aquisition date
- - Date written in the name
- - Last modification date
- Sort all file inside a directory by their Extension
- Sort by File Type [Video, Documents, Music, Images, Archives, Executables, Other]
- Dry run 

## Extract all files
The behaviour of this command will change depending on where you execute it.

- From directory background -> it will extract all files inside any subdirectory and move them in the one you are currently in
- Accessing the context menu by clinking on a folder, for example `folder1`, will present you two options:
1) `Extract all inside` -> It will extract all files inside any subdirectory of `folder` and move them inside `folder1`. It's the same as executing `Extract all files` from the directory background of `folder1`
2) `Extract all outside` -> It will extract all files inside any subdirectory of `folder` and move them outside of `folder1`, in its parent folder

## Sort by Date:
The script sorts the files by their dates. For each option (Acquisition date, date written in the name, last modification date) there are three possible folder structures:
- YYYY
- YYYY/mm
- YYYY/mm/dd

`Acquisition date` is a metadata included by Windows either by parsing the date in the name or using the creation date, but is not always present and is not always accurate. 

The date from the name is taken using the following regex
- `([1-2]\d\d\d)-?([0-1]\d)-?([0-3]\d)[_\-: T]?([0-2]\d):?([0-6]\d):?([0-6]\d)`
- and if it fails `([1-2]\d\d\d)-?([0-1]\d)-?([0-3]\d)`

The first try to match some variations of the format `YYYY-mm-dd HH:MM:SS`, while the second only `YYYY-mm-dd`.
I think this option is the most reliable one to sort images taken by a smartphone or a camera, as nearly all of them have the date written in the name following the ISO standard.
If you need a custom regex, add it in the following [function](https://github.com/Alessandro201/Context-menu-for-directory-organization/blob/7a4eb33d36ef939ae4ae13fec48d5c9242251c3a/functions/Sort.py#LL419C1-L432C73) in `functions/sort.py`:

```py
def find_dest_paths_by_date_in_name(file_paths: List[str], dest: Union[str, Path], strftime: str):
    # [...]
    
    POSSIBLE_REGEX = [re.compile('([1-2]\d\d\d)-?([0-1]\d)-?([0-3]\d)[_\-: T]?([0-2]\d):?([0-6]\d):?([0-6]\d)'),
                      re.compile('([1-2]\d\d\d)-?([0-1]\d)-?([0-3]\d)')]
```

## Sort by Extension
This command will sort the files in folders depending on their extension. Each extension will have it's own folder, and every file inside them will have **THE ORIGINAL FOLDER STRUCTURE PRESERVED**.

```
FOLDER
│
│   file1.jpg
│   file2.txt
|
├───folder1
│       file inside folder1.jpg
│
└───folder2
        file inside folder2.jpg
        file inside folder2.mp3
```

Becomes:
```
FOLDER
│
├───JPG
│   │   file1.jpg
│   │
│   ├───folder1
│   │       file inside folder1.jpg
│   │
│   └───folder2
│           file inside folder2.jpg
│
├───MP3
│   └───folder2
│           file inside folder2.mp3
│
└───TXT
        file2.txt
```

### Sort by File Type

```py
FILE_TYPES = {
    'Video': {'mp4', 'wmv', 'mkv', 'mpeg', 'webm', 'flv', 'avi', '3gp'},
    'Documents': {'txt', 'docx', 'doc', 'ppt', 'pdf', 'latex'},
    'Music': {'wav', 'mp3', 'flac', 'ogg', 'aac', 'opus', 'm4a'},
    'Images': {'jpg', 'jpeg', 'png', 'raw', 'dng', 'nef', 'tiff'},
    'Archives': {'rar', 'zip', '7z', '7zip', 'tar', 'gz'},
    'Executables': {'exe', 'sh', 'msi', 'apk', 'pkg'},
}
```

### Dry Run
In the context menu there are two options `enable dry run` and `disable dry run`. They work repectively by creating an empty file called `ENABLE_DRY_RUN` in the directory where the command will work, and deleting it.
**YOU MUST RUN THE COMMAND FROM THE SAME FOLDER YOU RUN** `enable dry run`.

##### Enabling dry mode from the directory background
![1](https://github.com/Alessandro201/Sort-ContextMenu/assets/61567683/6ca09dc2-20d0-4228-a1ea-b7eac8afd285)
![2](https://github.com/Alessandro201/Sort-ContextMenu/assets/61567683/8304fd64-7697-4877-ae12-8a83d427e206)

##### Enabling dry mode by cliking on a directory
![4](https://github.com/Alessandro201/Sort-ContextMenu/assets/61567683/7097fb98-8b57-4354-a404-10dcc1523c00)
![3](https://github.com/Alessandro201/Sort-ContextMenu/assets/61567683/0e21af07-0e07-4263-af3d-408b3f048ea2)


