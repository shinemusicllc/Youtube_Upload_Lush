using BaseSource.Data.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace BaseSource.Data.Configurations
{
    public class ChannelYoutubeConfiguration : IEntityTypeConfiguration<ChannelYoutube>
    {
        public void Configure(EntityTypeBuilder<ChannelYoutube> builder)
        {
            builder.ToTable("ChannelYoutubes");

            builder.HasKey(x => x.Id);
            builder.Property(x => x.Name).HasMaxLength(255);
            builder.Property(x => x.Avatar).HasMaxLength(255);
            builder.Property(x => x.ChannelYTId).HasMaxLength(255);
            builder.Property(x => x.Gmail).HasMaxLength(255);

            builder.HasOne(x => x.ManagerBOT).WithMany(x => x.ChannelYoutubes).HasForeignKey(x => x.ManagerBOTId);
        }
    }
}
