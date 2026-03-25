using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.SharedSignalrData.Classes
{
    public class PingData
    {
        /// <summary>
        /// bytes
        /// </summary>
        public long StorageCurrent { get; set; }
        /// <summary>
        /// bytes
        /// </summary>
        public long StorageTotal { get; set; }
        /// <summary>
        /// KB/s
        /// </summary>
        public double Bandwidth { get; set; }
    }
}
