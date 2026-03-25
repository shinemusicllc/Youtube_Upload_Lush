using BaseSource.ViewModels.Setting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BaseSource.Services.Services.Setting
{
    public interface IConfigSettingService
    {
        Task<ConfigSettingVm> GetSettingAsync();
        Task<KeyValuePair<bool, string>> UpdateAsync(ConfigSettingVm model);
    }
}
