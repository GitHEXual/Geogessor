import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import imageReducer from './slices/imageSlice';
import coordinatesReducer from './slices/coordinatesSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    image: imageReducer,
    coordinates: coordinatesReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
