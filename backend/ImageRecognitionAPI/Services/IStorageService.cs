namespace ImageRecognitionAPI.Services;

public interface IStorageService
{
    Task<string> UploadFileAsync(Stream fileStream, string fileName, string contentType);
    Task<Stream> DownloadFileAsync(string objectName);
    Task DeleteFileAsync(string objectName);
    Task<string> GetFileUrlAsync(string objectName, int expirySeconds = 3600);
}



