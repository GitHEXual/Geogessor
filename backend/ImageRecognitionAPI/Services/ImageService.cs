using AutoMapper;
using ImageRecognitionAPI.Data.Repositories;
using ImageRecognitionAPI.Models.DTOs;
using ImageRecognitionAPI.Models.Entities;

namespace ImageRecognitionAPI.Services;

public class ImageService : IImageService
{
    private readonly IImageRepository _imageRepository;
    private readonly IStorageService _storageService;
    private readonly IMapper _mapper;
    private readonly IConfiguration _configuration;

    public ImageService(
        IImageRepository imageRepository, 
        IStorageService storageService, 
        IMapper mapper,
        IConfiguration configuration)
    {
        _imageRepository = imageRepository;
        _storageService = storageService;
        _mapper = mapper;
        _configuration = configuration;
    }

    public async Task<ImageDto> UploadImageAsync(Guid userId, IFormFile file)
    {
        if (file == null || file.Length == 0)
            throw new ArgumentException("File is required and cannot be empty");

        // Validate file type
        var allowedTypes = new[] { "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp" };
        if (!allowedTypes.Contains(file.ContentType.ToLower()))
            throw new ArgumentException($"File type {file.ContentType} is not allowed. Allowed types: {string.Join(", ", allowedTypes)}");

        // Validate file size (e.g., max 10MB)
        const long maxFileSize = 10 * 1024 * 1024;
        if (file.Length > maxFileSize)
            throw new ArgumentException($"File size exceeds maximum allowed size of {maxFileSize / (1024 * 1024)}MB");

        using var stream = file.OpenReadStream();
        var objectName = await _storageService.UploadFileAsync(stream, file.FileName, file.ContentType);

        var image = new Image
        {
            Id = Guid.NewGuid(),
            FileName = file.FileName,
            OriginalFileName = file.FileName,
            ContentType = file.ContentType,
            SizeInBytes = file.Length,
            MinioObjectName = objectName,
            UserId = userId,
            UploadedAt = DateTime.UtcNow
        };

        await _imageRepository.CreateAsync(image);

        var imageDto = _mapper.Map<ImageDto>(image);
        imageDto.DownloadUrl = await _storageService.GetFileUrlAsync(objectName);
        
        return imageDto;
    }

    public async Task<List<ImageDto>> GetUserImagesAsync(Guid userId)
    {
        var images = await _imageRepository.GetByUserIdAsync(userId);
        var imageDtos = _mapper.Map<List<ImageDto>>(images);

        foreach (var imageDto in imageDtos)
        {
            var image = images.First(i => i.Id == imageDto.Id);
            imageDto.DownloadUrl = await _storageService.GetFileUrlAsync(image.MinioObjectName);
        }

        return imageDtos;
    }

    public async Task<ImageDto?> GetImageByIdAsync(Guid imageId)
    {
        var image = await _imageRepository.GetByIdAsync(imageId);
        if (image == null) return null;

        var imageDto = _mapper.Map<ImageDto>(image);
        imageDto.DownloadUrl = await _storageService.GetFileUrlAsync(image.MinioObjectName);
        
        return imageDto;
    }

    public async Task DeleteImageAsync(Guid imageId, Guid userId)
    {
        var image = await _imageRepository.GetByIdAsync(imageId);
        if (image == null)
            throw new KeyNotFoundException($"Image with id {imageId} not found");
        
        if (image.UserId != userId)
            throw new UnauthorizedAccessException("You do not have permission to delete this image");

        await _storageService.DeleteFileAsync(image.MinioObjectName);
        await _imageRepository.DeleteAsync(imageId);
    }

    public async Task<Stream> DownloadImageAsync(Guid imageId, Guid userId)
    {
        var image = await _imageRepository.GetByIdAsync(imageId);
        if (image == null)
            throw new KeyNotFoundException($"Image with id {imageId} not found");
        
        if (image.UserId != userId)
            throw new UnauthorizedAccessException("You do not have permission to download this image");

        return await _storageService.DownloadFileAsync(image.MinioObjectName);
    }
}



