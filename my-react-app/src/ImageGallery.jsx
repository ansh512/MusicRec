import React from 'react';

const ImageGallery = ({ imageUrls }) => {
  return (
    <div className="grid grid-cols-3 gap-4">
      {imageUrls.map((imageUrl, index) => (
        <div key={index} className="overflow-hidden relative group">
          <img
            src={imageUrl}
            alt={`Image ${index + 1}`}
            className="transition-transform duration-300 transform scale-100 group-hover:scale-110 hover:opacity-75 w-full h-64 object-cover"
          />
          <div className="absolute inset-0 bg-black bg-opacity-50 transition-opacity duration-300 opacity-0 group-hover:opacity-100 flex items-center justify-center">
            <p className="text-white font-bold">Image {index + 1}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ImageGallery;
