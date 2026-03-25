using BaseSource.SharedSignalrData.Enums;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.SharedSignalrData.Classes
{
    public class FileData
    {
        public long? Size { get; set; }
        public string Name { get; set; }
        public string Url { get; set; }
        public UrlType UrlType { get; set; } = UrlType.GoogleDrive;
        public FileType FileType { get; set; }
        public FilePosition FilePosition { get; set; }
    }
}
