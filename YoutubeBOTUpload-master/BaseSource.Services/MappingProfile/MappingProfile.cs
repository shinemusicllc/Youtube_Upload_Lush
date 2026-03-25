using AutoMapper;
using BaseSource.ViewModels.User;
using BaseSource.Data.Entities;
using BaseSource.ViewModels.Render;
using BaseSource.ViewModels.Setting;

namespace BaseSource.Services.MappingProfile
{
    public class MappingProfile : Profile
    {
        public MappingProfile()
        {

            #region User

            CreateMap<AppUser, UserInfoResponse>();
            #endregion

            #region Render 
            CreateMap<RenderHistory, RenderHistoryDto>()
                .ForMember(dest => dest.ChannelId, options => options.MapFrom(source => source.ChannelYoutubeId))
                .ForMember(dest => dest.ChannelYTId, options => options.MapFrom(source => source.ChannelYoutube.ChannelYTId))
                .ForMember(dest => dest.ChannelName, options => options.MapFrom(source => source.ChannelYoutube.Name))
                .ForMember(dest => dest.BotName, options => options.MapFrom(source => source.ChannelYoutube.ManagerBOT.Name))
                .ForMember(dest => dest.Group, options => options.MapFrom(source => source.ChannelYoutube.ManagerBOT.Group))
                .ForMember(dest => dest.Avatar, options => options.MapFrom(source => source.ChannelYoutube.Avatar))
                .ForMember(dest => dest.VideoLink, options => options.MapFrom(source => source.VideoLink));

            #endregion

            #region ConfigSystem

            CreateMap<ConfigSystem, ConfigSettingVm>();
            #endregion
        }

    }
}
