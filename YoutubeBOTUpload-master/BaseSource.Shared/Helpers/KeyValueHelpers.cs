using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.Shared.Helpers
{
   public class MyKeyValuePair<TKey, TValue>
    {
        public TKey Key { get; }
        public TValue Value { get; }
        public MyKeyValuePair(TKey key, TValue value)
        {
            this.Key = key;
            this.Value = value;
        }
        //public static explicit operator BoolStringKeyValuePair<TKey,TValue>(TKey result) => new BoolStringKeyValuePair<TKey,TValue>(result,default(TValue));
    }
   public class BoolStringKeyValuePair : MyKeyValuePair<bool, string>
    {
        public BoolStringKeyValuePair(bool key, string value) : base(key, value) { }
        public static implicit operator BoolStringKeyValuePair(bool result) => new BoolStringKeyValuePair(result, string.Empty);
        public static implicit operator BoolStringKeyValuePair(string message) => new BoolStringKeyValuePair(false, message);
        public static implicit operator bool(BoolStringKeyValuePair pair) => pair.Key;
    }
}
