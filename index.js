const topicsContainer = document.querySelector('#Topics');
const openingContainer = document.querySelector('#Opening');
const sectionContainer = document.querySelectorAll('#Sections');
const sections = document.querySelectorAll('.Section');
const resetButton = document.querySelector('h1');
const sectionHeaders = document.querySelectorAll('h3');

topicsContainer.addEventListener('click', e => {
    topicsContainer.classList.toggle('Active');
    const id = e.target.dataset?.section;
    const isActive = topicsContainer.classList.contains('Active')
    if (!isActive && !id) reset();
}, false);

const selectTopic = sectionId => {
    const currentSection = [...sections].find(s => s.classList.contains('Visible'));
    if (currentSection) currentSection?.classList.remove('Visible');
    if (!currentSection) openingContainer.classList.add('Hidden');
    const sectionToSelect = [...sections].find(s => s.dataset.section === sectionId);
    if (sectionToSelect) {
        const images = sectionToSelect.querySelectorAll('div');
        console.log([...images].map(i => i.dataset.link));
        images.forEach(imageContainer => {
            const img = document.createElement("img");
            img.src = imageContainer.dataset.link.replace('/img/', '/img-thumb/');
            const thumb = document.createElement("button");
            imageContainer.innerHTML = '';
            thumb.innerText = '📷'
            imageContainer.appendChild(thumb);
            imageContainer.appendChild(img);
            const instance =  Popper.createPopper(thumb, img, {
                // options
              });
            setInterval(() => {
                instance.update();
            }, 1000);
        });
        sectionToSelect.classList.add('Visible');
    };
};

const reset = () => {
    const currentSection = [...sections].find(s => s.classList.contains('Visible'));
    if (currentSection) currentSection?.classList.remove('Visible');
    openingContainer.classList.remove('Hidden');
};

[...sectionHeaders].forEach(h => h.addEventListener('click', e => {
    selectTopic(e.target.dataset.section);
}, false));
