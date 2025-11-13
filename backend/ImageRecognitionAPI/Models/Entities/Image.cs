namespace ImageRecognitionAPI.Models.Entities;

public class Image
{
    public Guid Id { get; set; }
    public string FileName { get; set; } = string.Empty;
    public string OriginalFileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;
    public long SizeInBytes { get; set; }
    public string MinioObjectName { get; set; } = string.Empty;
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
    
    // Foreign key
    public Guid UserId { get; set; }
    public User User { get; set; } = null!;
}



