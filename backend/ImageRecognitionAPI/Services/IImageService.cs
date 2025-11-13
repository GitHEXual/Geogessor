using ImageRecognitionAPI.Models.DTOs;

namespace ImageRecognitionAPI.Services;

public interface IImageService
{
    Task<ImageDto> UploadImageAsync(Guid userId, IFormFile file);
    Task<List<ImageDto>> GetUserImagesAsync(Guid userId);
    Task<ImageDto?> GetImageByIdAsync(Guid imageId);
    Task DeleteImageAsync(Guid imageId, Guid userId);
    Task<Stream> DownloadImageAsync(Guid imageId, Guid userId);
}



