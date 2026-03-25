using AutoMapper;
using BaseSource.Data.EF;
using BaseSource.Data.Entities;
using BaseSource.ViewModels.Setting;
using EFCore.UnitOfWork;
using Microsoft.Extensions.Logging;

namespace BaseSource.Services.Services.Setting
{
    public class ConfigSettingService : IConfigSettingService
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly ILogger<ConfigSettingService> _logger;
        private readonly IMapper _mapper;

        public ConfigSettingService(IUnitOfWork<BaseSourceDbContext> unitOfWork,
            ILogger<ConfigSettingService> logger, IMapper mapper)
        {
            _unitOfWork = unitOfWork;
            _logger = logger;
            _mapper = mapper;
        }
        public async Task<ConfigSettingVm> GetSettingAsync()
        {
            var _repository = _unitOfWork.GetRepository<ConfigSystem>();
            return await _repository.GetFirstOrDefaultAsync(
                selector: x => _mapper.Map<ConfigSettingVm>(x));
        }

        public async Task<KeyValuePair<bool, string>> UpdateAsync(ConfigSettingVm model)
        {
            try
            {
                var _repository = _unitOfWork.GetRepository<ConfigSystem>();
                var settingEntity = await _repository.GetFirstOrDefaultAsync(disableTracking: false);
                if (settingEntity != null)
                {
                    settingEntity.BankNumber = model.BankNumber;
                    settingEntity.LinkYoutube = model.LinkYoutube;
                    settingEntity.LinkFBAdmin = model.LinkFBAdmin;
                    settingEntity.BankName = model.BankName;
                    settingEntity.BankAccountName = model.BankAccountName;
                    _repository.Update(settingEntity);
                    await _unitOfWork.SaveChangesAsync();
                }
                return new KeyValuePair<bool, string>(true, string.Empty);

            }
            catch (Exception ex)
            {
                _logger.LogError($"Update Config failed by error:[{ex}]");
                return new KeyValuePair<bool, string>(false, "Cập nhật không thành công!");
            }
        }
    }
}
