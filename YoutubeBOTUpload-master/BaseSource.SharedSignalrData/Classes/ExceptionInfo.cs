using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.SharedSignalrData.Classes
{
    public class ExceptionInfo
    {
        public ExceptionInfo()
        {

        }
        public ExceptionInfo(Exception exception)
        {
            if (exception is null) throw new ArgumentNullException(nameof(exception));
            this.Name = exception.GetType().Name;
            this.FullName = exception.GetType().FullName;
            this.Message = exception.Message;
            this.StackTrace = exception.StackTrace;
        }
        public string Name { get; set; }
        public string FullName { get; set; }
        public string Message { get; set; }
        public string StackTrace { get; set; }
    }
}
