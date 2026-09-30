// Club Med French Alps ski resorts tracked daily. `id` matches the price data.
export interface Resort {
  id: string; slug: string; name: string; fullName: string; area: string; altitude: string;
  image: string; imageAlt: string; bookingUrl: string; blog?: string;
}

export const RESORTS: Resort[] = [
  { id: 'tignes-val-claret', slug: 'tignes', name: 'Tignes', fullName: 'Club Med Tignes', area: "Espace Killy", altitude: '2,100m', image: 'Tignes', imageAlt: 'Snow-covered slopes above Tignes', bookingUrl: 'https://www.clubmed.co.uk/r/tignes/w', blog: 'best-time-to-book-club-med-tignes' },
  { id: 'val-thorens', slug: 'val-thorens', name: 'Val Thorens', fullName: 'Club Med Val Thorens Sensations', area: 'Three Valleys', altitude: '2,300m', image: 'Val-Thorens', imageAlt: 'Val Thorens resort in winter', bookingUrl: 'https://www.clubmed.co.uk/r/val-thorens-sensations/w', blog: 'best-time-to-book-club-med-val-thorens' },
  { id: 'val-disere', slug: 'val-disere', name: "Val d'Isère", fullName: "Club Med Val d'Isère", area: 'Espace Killy', altitude: '1,850m', image: 'Val-Disere', imageAlt: "Val d'Isère village under snow", bookingUrl: 'https://www.clubmed.co.uk/r/val-disere/w', blog: 'best-time-to-book-club-med-val-disere' },
  { id: 'les-arcs', slug: 'les-arcs', name: 'Les Arcs', fullName: 'Club Med Les Arcs Panorama', area: 'Paradiski', altitude: '1,950m', image: 'Les-Arcs', imageAlt: 'Les Arcs ski area', bookingUrl: 'https://www.clubmed.co.uk/r/les-arcs/w', blog: 'best-time-to-book-club-med-les-arcs' },
  { id: 'la-plagne-2100', slug: 'la-plagne', name: 'La Plagne', fullName: 'Club Med La Plagne 2100', area: 'Paradiski', altitude: '2,100m', image: 'La-plagne', imageAlt: 'La Plagne in winter', bookingUrl: 'https://www.clubmed.co.uk/r/la-plagne-2100/y', blog: 'best-time-to-book-club-med-la-plagne' },
  { id: 'peisey-vallandry', slug: 'peisey-vallandry', name: 'Peisey-Vallandry', fullName: 'Club Med Peisey-Vallandry', area: 'Paradiski', altitude: '1,600m', image: 'Peisey-Vallandry', imageAlt: 'Peisey-Vallandry forest slopes', bookingUrl: 'https://www.clubmed.co.uk/r/peisey-vallandry/w', blog: 'best-time-to-book-club-med-peisey-vallandry' },
  { id: 'alpe-dhuez', slug: 'alpe-dhuez', name: "Alpe d'Huez", fullName: "Club Med Alpe d'Huez", area: 'Oisans', altitude: '1,860m', image: 'Alpe-dhuez', imageAlt: "Alpe d'Huez ski slopes", bookingUrl: 'https://www.clubmed.co.uk/r/alpe-dhuez/w', blog: 'best-time-to-book-club-med-alpe-dhuez' },
  { id: 'la-rosiere', slug: 'la-rosiere', name: 'La Rosière', fullName: 'Club Med La Rosière', area: 'Espace San Bernardo', altitude: '1,850m', image: 'La-Rosiere', imageAlt: 'La Rosière in winter', bookingUrl: 'https://www.clubmed.co.uk/r/la-rosiere/w', blog: 'best-time-to-book-club-med-la-rosiere' },
  { id: 'valmorel', slug: 'valmorel', name: 'Valmorel', fullName: 'Club Med Valmorel', area: 'Grand Domaine', altitude: '1,460m', image: 'Valmorel', imageAlt: 'Valmorel resort and slopes', bookingUrl: 'https://www.clubmed.co.uk/r/valmorel/w', blog: 'best-time-to-book-club-med-valmorel' },
  { id: 'grand-massif', slug: 'grand-massif', name: 'Grand Massif', fullName: 'Club Med Grand Massif Samoëns Morillon', area: 'Grand Massif', altitude: '', image: 'Grand-Massif', imageAlt: 'Grand Massif mountains', bookingUrl: 'https://www.clubmed.co.uk/r/grand-massif/w', blog: 'best-time-to-book-club-med-grand-massif' },
  { id: 'serre-chevalier', slug: 'serre-chevalier', name: 'Serre-Chevalier', fullName: 'Club Med Serre-Chevalier', area: 'Southern Alps', altitude: '1,400m', image: 'Serre-chevalier', imageAlt: 'Serre-Chevalier valley in winter', bookingUrl: 'https://www.clubmed.co.uk/r/serre-chevalier/w', blog: 'best-time-to-book-club-med-serre-chevalier' },
];
