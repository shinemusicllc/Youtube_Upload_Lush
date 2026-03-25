using BaseSource.Data.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BaseSource.Data.Configurations
{
    public class RenderHistoryConfiguration : IEntityTypeConfiguration<RenderHistory>
    {
        public void Configure(EntityTypeBuilder<RenderHistory> builder)
        {
            builder.ToTable("RenderHistorys");

            builder.HasKey(x => x.Id);
            builder.Property(x => x.Intro).HasMaxLength(255);
            builder.Property(x => x.VideoLoop).HasMaxLength(255);
            builder.Property(x => x.AudioLoop).HasMaxLength(255);
            builder.Property(x => x.Outtro).HasMaxLength(255);
            builder.Property(x => x.VideoName).HasMaxLength(255);
            builder.Property(x => x.ErrorMessage).HasMaxLength(500);

            builder.HasOne(x => x.ChannelYoutube).WithMany(x => x.RenderHistorys).HasForeignKey(x => x.ChannelYoutubeId);
            builder.HasOne(x => x.AppUser).WithMany(x => x.RenderHistorys).HasForeignKey(x => x.UserId);
        }
    }
}
