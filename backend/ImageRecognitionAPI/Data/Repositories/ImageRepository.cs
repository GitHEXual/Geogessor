using ImageRecognitionAPI.Models.Entities;
using Microsoft.EntityFrameworkCore;

namespace ImageRecognitionAPI.Data.Repositories;

public class ImageRepository : IImageRepository
{
    private readonly ApplicationDbContext _context;

    public ImageRepository(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<Image?> GetByIdAsync(Guid id)
    {
        return await _context.Images
            .Include(i => i.User)
            .FirstOrDefaultAsync(i => i.Id == id);
    }

    public async Task<List<Image>> GetByUserIdAsync(Guid userId)
    {
        return await _context.Images
            .Where(i => i.UserId == userId)
            .OrderByDescending(i => i.UploadedAt)
            .ToListAsync();
    }

    public async Task<Image> CreateAsync(Image image)
    {
        _context.Images.Add(image);
        await _context.SaveChangesAsync();
        return image;
    }

    public async Task DeleteAsync(Guid id)
    {
        var image = await GetByIdAsync(id);
        if (image != null)
        {
            _context.Images.Remove(image);
            await _context.SaveChangesAsync();
        }
    }

    public async Task<bool> IsOwnerAsync(Guid imageId, Guid userId)
    {
        return await _context.Images
            .AnyAsync(i => i.Id == imageId && i.UserId == userId);
    }
}



