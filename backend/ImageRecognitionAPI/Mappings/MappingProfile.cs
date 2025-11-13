using AutoMapper;
using ImageRecognitionAPI.Models.DTOs;
using ImageRecognitionAPI.Models.Entities;

namespace ImageRecognitionAPI.Mappings;

public class MappingProfile : Profile
{
    public MappingProfile()
    {
        CreateMap<User, UserDto>()
            .ForMember(dest => dest.Role, opt => opt.MapFrom(src => src.Role.ToString()))
            .ForMember(dest => dest.Status, opt => opt.MapFrom(src => src.Status.ToString()));

        CreateMap<Image, ImageDto>()
            .ForMember(dest => dest.DownloadUrl, opt => opt.Ignore());
    }
}



