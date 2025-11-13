using ImageRecognitionAPI.Models.Entities;

namespace ImageRecognitionAPI.Data.Repositories;

public interface IImageRepository
{
    Task<Image?> GetByIdAsync(Guid id);
    Task<List<Image>> GetByUserIdAsync(Guid userId);
    Task<Image> CreateAsync(Image image);
    Task DeleteAsync(Guid id);
    Task<bool> IsOwnerAsync(Guid imageId, Guid userId);
}



