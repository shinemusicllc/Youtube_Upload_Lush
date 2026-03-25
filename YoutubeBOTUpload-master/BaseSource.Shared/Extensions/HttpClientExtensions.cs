using BaseSource.Shared.Helpers;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.Shared.Extensions
{
    public static class HttpClientExtensions
    {

        public static async Task<T> PostAsync<T>(this HttpClient client, string url, object data = null)
        {
            var json = JsonConvert.SerializeObject(data);
            using (var content = new StringContent(json, Encoding.UTF8, "application/json"))
            {
                using (var response = await client.PostAsync(url, content))
                {
                    var responseString = await response.Content.ReadAsStringAsync();
                    var result = JsonConvert.DeserializeObject<T>(responseString);
                    return result;
                }
            }
        }

        public static async Task<T> PostAsyncFormUrl<T>(this HttpClient client, string url, Dictionary<string, string> data)
        {
            using (var content = new FormUrlEncodedContent(data))
            {
                using (var response = await client.PostAsync(url, content))
                {
                    var responseString = await response.Content.ReadAsStringAsync();
                    var result = JsonConvert.DeserializeObject<T>(responseString);
                    return result;
                }
            }
        }

        public static async Task<T> GetAsync<T>(this HttpClient client, string url, object data = null)
        {
            if (data != null)
            {
                string queryString = UrlHelper.GetQueryString(data);
                url += "?" + queryString;
            }

            using (var response = await client.GetAsync(url))
            {
                var responseString = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<T>(responseString);
                return result;
            }
        }

        public static async Task<T> PutAsync<T>(this HttpClient client, string url, object data)
        {
            var json = JsonConvert.SerializeObject(data);
            using (var content = new StringContent(json, Encoding.UTF8, "application/json"))
            {
                using (var response = await client.PutAsync(url, content))
                {
                    var responseString = await response.Content.ReadAsStringAsync();
                    var result = JsonConvert.DeserializeObject<T>(responseString);
                    return result;
                }
            }
        }

#if NET6_0_OR_GREATER
        public static async Task<T> PatchAsync<T>(this HttpClient client, string url, object data = null)
        {
            var json = data == null ? string.Empty : JsonConvert.SerializeObject(data);
            using (var content = new StringContent(json, Encoding.UTF8, "application/json"))
            {
                using (var response = await client.PatchAsync(url, content))
                {
                    var responseString = await response.Content.ReadAsStringAsync();
                    var result = JsonConvert.DeserializeObject<T>(responseString);
                    return result;
                }
            }
        }
#endif

        public static async Task<T> DeleteAsync<T>(this HttpClient client, string url)
        {
            using (var response = await client.DeleteAsync(url))
            {
                var responseString = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<T>(responseString);
                return result;
            }
        }
    }
}
