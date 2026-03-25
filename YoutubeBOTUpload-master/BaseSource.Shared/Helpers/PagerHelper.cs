using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.Shared.Helpers
{
    public static class PagerHelper
    {
        public static string ConvertToUrlString(this IQueryCollection query, string urlTemplate, string[] excepts = null)
        {
            if (string.IsNullOrEmpty(urlTemplate))
            {
                urlTemplate = "";
            }

            if (!urlTemplate.Contains("?"))
            {
                urlTemplate += "?";
            }

            foreach (var key in query.Keys)
            {
                if (excepts != null)
                {
                    excepts = excepts.Select(selector: x => x.ToLower()).ToArray();
                    if (excepts.Contains(key.ToLower())) /*key == "page" || key == "pageSize" || key == "sort"*/
                    {
                        continue;
                    }
                }
                if (query[key].Count > 1)
                {
                    foreach (var item in (string[])query[key])
                    {
                        if (!urlTemplate.EndsWith("?"))
                        {
                            urlTemplate += "&";
                        }

                        urlTemplate += key + "=" + item;
                    }
                }
                else
                {
                    if (!urlTemplate.EndsWith("?"))
                    {
                        urlTemplate += "&";
                    }

                    urlTemplate += key + "=" + query[key];
                }
            }

            return urlTemplate;
        }

    }
}
