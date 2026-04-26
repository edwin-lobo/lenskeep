import React, { useMemo, useState } from 'react';

type NutritionGoal = 'fat_loss' | 'maintenance' | 'muscle_gain';
type ActivityLevel = 'light' | 'moderate' | 'high';
type SexAtBirth = 'female' | 'male';

type MacroPlan = {
  calories: number;
  proteinRange: [number, number];
  carbRange: [number, number];
  fatRange: [number, number];
  hydrationLiters: number;
  fiberGoal: number;
};

const goalLabels: Record<NutritionGoal, string> = {
  fat_loss: 'Fat loss',
  maintenance: 'Maintenance',
  muscle_gain: 'Muscle gain',
};

const activityMultiplier: Record<ActivityLevel, number> = {
  light: 1.4,
  moderate: 1.6,
  high: 1.8,
};

const carbTargetsByActivity: Record<ActivityLevel, [number, number]> = {
  light: [3, 5],
  moderate: [4, 6],
  high: [5, 8],
};

const goalCalorieAdjustments: Record<NutritionGoal, number> = {
  fat_loss: -400,
  maintenance: 0,
  muscle_gain: 250,
};

const goalProteinTargets: Record<NutritionGoal, [number, number]> = {
  fat_loss: [1.8, 2.4],
  maintenance: [1.6, 2.2],
  muscle_gain: [1.6, 2.2],
};

const NutritionPlanner: React.FC = () => {
  const [weightKg, setWeightKg] = useState(78);
  const [heightCm, setHeightCm] = useState(175);
  const [age, setAge] = useState(30);
  const [sexAtBirth, setSexAtBirth] = useState<SexAtBirth>('male');
  const [activityLevel, setActivityLevel] = useState<ActivityLevel>('moderate');
  const [goal, setGoal] = useState<NutritionGoal>('maintenance');

  const plan: MacroPlan = useMemo(() => {
    const bmr =
      sexAtBirth === 'male'
        ? 10 * weightKg + 6.25 * heightCm - 5 * age + 5
        : 10 * weightKg + 6.25 * heightCm - 5 * age - 161;

    const estimatedMaintenance = bmr * activityMultiplier[activityLevel];
    const calories = Math.max(1400, Math.round(estimatedMaintenance + goalCalorieAdjustments[goal]));

    const proteinRange: [number, number] = [
      Math.round(goalProteinTargets[goal][0] * weightKg),
      Math.round(goalProteinTargets[goal][1] * weightKg),
    ];

    const carbRange: [number, number] = [
      Math.round(carbTargetsByActivity[activityLevel][0] * weightKg),
      Math.round(carbTargetsByActivity[activityLevel][1] * weightKg),
    ];

    const minFatFromCalories = Math.round((calories * 0.2) / 9);
    const maxFatFromCalories = Math.round((calories * 0.35) / 9);
    const fatRange: [number, number] = [minFatFromCalories, maxFatFromCalories];

    const hydrationLiters = sexAtBirth === 'male' ? 3.7 : 2.7;
    const fiberGoal = Math.round((14 * calories) / 1000);

    return {
      calories,
      proteinRange,
      carbRange,
      fatRange,
      hydrationLiters,
      fiberGoal,
    };
  }, [age, activityLevel, goal, heightCm, sexAtBirth, weightKg]);

  return (
    <section id="nutrition" className="mx-auto max-w-6xl px-6 py-16">
      <div className="mb-8 max-w-3xl space-y-4">
        <div className="pill w-fit">Nutrition planning</div>
        <h2 className="text-3xl font-bold text-slate-900 md:text-4xl">Build a tailored fueling plan in minutes</h2>
        <p className="text-lg text-slate-600">
          This starter plan follows widely adopted sports-nutrition guidance: adequate protein, activity-matched carbs,
          minimum fat intake, hydration targets, and realistic calorie adjustments.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
        <article className="card p-6">
          <h3 className="text-lg font-semibold text-slate-900">Profile inputs</h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <label className="text-sm text-slate-700">
              Weight (kg)
              <input
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                type="number"
                min={40}
                max={220}
                value={weightKg}
                onChange={(event) => setWeightKg(Number(event.target.value) || 40)}
              />
            </label>
            <label className="text-sm text-slate-700">
              Height (cm)
              <input
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                type="number"
                min={130}
                max={230}
                value={heightCm}
                onChange={(event) => setHeightCm(Number(event.target.value) || 130)}
              />
            </label>
            <label className="text-sm text-slate-700">
              Age
              <input
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                type="number"
                min={18}
                max={80}
                value={age}
                onChange={(event) => setAge(Number(event.target.value) || 18)}
              />
            </label>
            <label className="text-sm text-slate-700">
              Sex at birth
              <select
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={sexAtBirth}
                onChange={(event) => setSexAtBirth(event.target.value as SexAtBirth)}
              >
                <option value="female">Female</option>
                <option value="male">Male</option>
              </select>
            </label>
            <label className="text-sm text-slate-700">
              Activity level
              <select
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={activityLevel}
                onChange={(event) => setActivityLevel(event.target.value as ActivityLevel)}
              >
                <option value="light">Light (2-3 sessions/week)</option>
                <option value="moderate">Moderate (4-5 sessions/week)</option>
                <option value="high">High (6+ sessions/week)</option>
              </select>
            </label>
            <label className="text-sm text-slate-700">
              Goal
              <select
                className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2"
                value={goal}
                onChange={(event) => setGoal(event.target.value as NutritionGoal)}
              >
                <option value="fat_loss">Fat loss</option>
                <option value="maintenance">Maintenance</option>
                <option value="muscle_gain">Muscle gain</option>
              </select>
            </label>
          </div>
        </article>

        <article className="card p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">Daily targets</h3>
            <span className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700">
              {goalLabels[goal]}
            </span>
          </div>
          <dl className="mt-4 space-y-3 text-sm text-slate-700">
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
              <dt>Calories</dt>
              <dd className="font-semibold text-slate-900">{plan.calories.toLocaleString()} kcal</dd>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
              <dt>Protein</dt>
              <dd className="font-semibold text-slate-900">
                {plan.proteinRange[0]}–{plan.proteinRange[1]} g
              </dd>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
              <dt>Carbohydrate</dt>
              <dd className="font-semibold text-slate-900">
                {plan.carbRange[0]}–{plan.carbRange[1]} g
              </dd>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
              <dt>Fat</dt>
              <dd className="font-semibold text-slate-900">
                {plan.fatRange[0]}–{plan.fatRange[1]} g
              </dd>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
              <dt>Fiber</dt>
              <dd className="font-semibold text-slate-900">≥ {plan.fiberGoal} g</dd>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
              <dt>Fluids</dt>
              <dd className="font-semibold text-slate-900">~ {plan.hydrationLiters.toFixed(1)} L + sweat losses</dd>
            </div>
          </dl>
          <p className="mt-4 text-xs leading-relaxed text-slate-500">
            This tool is educational and not medical care. Refer users with chronic disease, pregnancy, eating disorder risk,
            or rapid weight-change goals to a registered dietitian.
          </p>
        </article>
      </div>

      <article className="card mt-6 p-6">
        <h3 className="text-lg font-semibold text-slate-900">Best-practice checklist used by this planner</h3>
        <ul className="mt-4 grid gap-3 text-sm text-slate-700 md:grid-cols-2">
          <li>✔️ Protein is set by body mass (1.6–2.4 g/kg) to preserve or build lean mass.</li>
          <li>✔️ Carbs scale with training demand (3–8 g/kg/day) to support performance and recovery.</li>
          <li>✔️ Fat is held at a minimum 20–35% of calories for hormonal and nutrient needs.</li>
          <li>✔️ Fat-loss plans use moderate deficits (~300–500 kcal/day) to improve adherence and muscle retention.</li>
          <li>✔️ Fiber goal is set from energy intake (14 g per 1000 kcal).</li>
          <li>✔️ Base hydration aligns with sex-specific daily targets, plus training losses.</li>
        </ul>
      </article>
    </section>
  );
};

export default NutritionPlanner;
