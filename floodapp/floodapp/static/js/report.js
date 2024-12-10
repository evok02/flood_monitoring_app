document.addEventListener('DOMContentLoaded', () => {
    const regionSelect = document.getElementById('region');
    const cities = [
        { id: 1, name: 'Vienna' }
    ];

    cities.forEach(city => {
        const option = document.createElement('option');
        option.value = city.id;
        option.textContent = city.name;
        regionSelect.appendChild(option);
    });
});