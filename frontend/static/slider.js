$(document).ready(function(){
  const sliderImages = [
    "static/images/myLogo1.png",
    "https://i.pinimg.com/originals/18/69/1c/18691c19d0a3fea43be48d2b0a002a87.png",
    "https://t4.ftcdn.net/jpg/01/47/83/81/360_F_147838124_YZlIKudatjV5qSN1PmHDLKJSh2cm32nR.jpg",
    "https://png.pngtree.com/thumb_back/fh260/background/20230704/pngtree-stack-of-law-books-with-courtroom-scales-image_3721829.jpg",
    "https://archives1.dailynews.lk/sites/default/files/news/2022/10/05/GAYAN-CDN-L%26A-01.jpg",
    "https://c4.wallpaperflare.com/wallpaper/307/345/278/scales-wallpaper-preview.jpg",
  ];

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 2000,
    slidesToShow: 3,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 150,
  };

  const sliderContainer = $('#slider-container');
  sliderImages.forEach((imageUrl, index) => {
    const sliderDiv = $('<div class="slide-item"></div>');
    const sliderImg = $('<img>', {
      src: imageUrl,
      alt: `image ${index + 1}`,
      style: "width: 350px; height: 350px;"
    });
    sliderDiv.append(sliderImg);
    sliderContainer.append(sliderDiv);
  });

  sliderContainer.slick(sliderSettings);
});
