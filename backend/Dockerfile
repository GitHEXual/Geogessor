FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy csproj and restore dependencies
COPY ImageRecognitionAPI/ImageRecognitionAPI.csproj ImageRecognitionAPI/
RUN dotnet restore ImageRecognitionAPI/ImageRecognitionAPI.csproj

# Copy everything else and build
COPY . .
WORKDIR /src/ImageRecognitionAPI
RUN dotnet build ImageRecognitionAPI.csproj -c Release -o /app/build

FROM build AS publish
RUN dotnet publish ImageRecognitionAPI.csproj -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Install EF Core tools for migrations
RUN dotnet tool install --global dotnet-ef
ENV PATH="${PATH}:/root/.dotnet/tools"

EXPOSE 80
ENTRYPOINT ["dotnet", "ImageRecognitionAPI.dll"]



