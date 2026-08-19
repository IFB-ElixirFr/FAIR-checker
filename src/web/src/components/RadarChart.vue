<script setup>

    import {
      Chart as ChartJS,
      RadialLinearScale,
      PointElement,
      LineElement,
      Filler,
      Tooltip,
      Legend
    } from 'chart.js'
    
    import { Radar } from 'vue-chartjs'
    
    ChartJS.register(
      RadialLinearScale,
      PointElement,
      LineElement,
      Filler,
      Tooltip,
      Legend
    )
    
    const chartData = {
      labels: [
        'Findable',
        'Interoperable',
        'Reusable',
        'Accessible'
      ],
    
      datasets: [
        {
          label: 'Success',
    
          data: [0, 0, 0, 0],
    
          borderWidth: 2,
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(219, 242, 242, 0.5)',
    
          pointRadius: 5,
          pointHitRadius: 50,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)'
        }
      ]
    }
    
    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
    
      scales: {
        r: {
          min: 0,
          max: 100,
    
          ticks: {
            stepSize: 20
          }
        }
      },
    
      plugins: {
        tooltip: {
          callbacks: {
            title: (tooltipItems) => {
              return tooltipItems[0].label
            },
    
            label: (tooltipItem) => {
              return `${tooltipItem.raw} %`
            }
          }
        }
      },
    
      animation: {
        duration: 500
      }
    }
</script>

<template>
  <div style="width: 400px; height: 400px;">
    <Radar
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

