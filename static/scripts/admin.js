import Chart from "chart.js/auto";

const fileAPI       = "api/file";
const fileStatsAPI  = "api/file/stats";
const addUserAPI    = "api/user/create";
const deleteUserAPI = "api/user/delete";
const userAPI       = "api/user/search";
const pageViewAPI   = "api/pages/history";
const pageStatsAPI  = "api/pages"


async function createDownloadSummary(host) {
    let files = await fetch(`http://${host}/${fileAPI}/all?cols=all`);
    files = await files.json();
}


async function quickSummary(host) {
    createDownloadSummary(host)
    const ctx = document.getElementById('myChart');

      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
          datasets: [{
            label: '# of Votes',
            data: [12, 19, 3, 5, 2, 3],
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
}


quickSummary("192.168.0.200:5000")
