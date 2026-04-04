import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TrocarSenha } from './trocar-senha';

describe('TrocarSenha', () => {
    let component: TrocarSenha;
    let fixture: ComponentFixture<TrocarSenha>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [TrocarSenha],
        }).compileComponents();

        fixture = TestBed.createComponent(TrocarSenha);
        component = fixture.componentInstance;
        await fixture.whenStable();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
