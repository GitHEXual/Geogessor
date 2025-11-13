using ImageRecognitionAPI.Models.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ImageRecognitionAPI.Data.Configurations;

public class ImageConfiguration : IEntityTypeConfiguration<Image>
{
    public void Configure(EntityTypeBuilder<Image> builder)
    {
        builder.HasKey(i => i.Id);
        
        builder.Property(i => i.FileName)
            .IsRequired()
            .HasMaxLength(255);
        
        builder.Property(i => i.OriginalFileName)
            .IsRequired()
            .HasMaxLength(255);
        
        builder.Property(i => i.ContentType)
            .IsRequired()
            .HasMaxLength(100);
        
        builder.Property(i => i.SizeInBytes)
            .IsRequired();
        
        builder.Property(i => i.MinioObjectName)
            .IsRequired()
            .HasMaxLength(500);
        
        builder.Property(i => i.UploadedAt)
            .IsRequired();
        
        builder.HasOne(i => i.User)
            .WithMany(u => u.Images)
            .HasForeignKey(i => i.UserId)
            .OnDelete(DeleteBehavior.Cascade);
        
        builder.HasIndex(i => i.UserId);
    }
}



